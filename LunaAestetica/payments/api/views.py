# payments/api/views.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

import json

import stripe
from decimal import Decimal

from meets.models import Appointment
from payments.models import Wallet, Transaction
from payments.api.serializers import WalletSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
  if created:
    Wallet.objects.get_or_create(user=instance)

class WalletViewSet(viewsets.ReadOnlyModelViewSet):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = WalletSerializer

  def get_queryset(self):
    return Wallet.objects.filter(user=self.request.user)

  def list(self, request, *args, **kwargs):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    serializer = self.get_serializer(wallet)
    return Response(serializer.data)


class StripeCheckoutView(views.APIView):
  def post(self, request):
      
    try:

      data = request.data
      p_type = data.get('type') # 'APPOINTMENT' o 'WALLET_RELOAD'
      if data.get('amount'):

        amount_in_cents = int(data.get('amount'))
        amount_to_charge = Decimal(amount_in_cents) / 100

      else:

        appointment_ids = data.get('appointment_ids', [])
        appointments = Appointment.objects.filter(id__in=appointment_ids, customer=request.user)
        amount_to_charge = sum(app.remaining_amount for app in appointments)

      if amount_to_charge <= 0:

        return Response({'error': 'L\'importo deve essere maggiore di zero'}, status=400)

      metadata = {
        'customer_id': request.user.id,
        'type': p_type,
        'appointment_ids': ",".join(map(str, data.get('appointment_ids', []))) if data.get('appointment_ids') else ""
      }

      checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
          'price_data': {
            'currency': 'eur',
            'product_data': {
              'name': 'Pagamento Prenotazione' if p_type != 'WALLET_RELOAD' else 'Ricarica Wallet',
            },
            'unit_amount': int(amount_to_charge * 100),
          },
          'quantity': 1,
        }],
        mode='payment',
        metadata=metadata,
        success_url=settings.FRONTEND_URL + '/#/client-dashboard?payment=success',
        cancel_url=settings.FRONTEND_URL + '/#/client-dashboard?payment=cancel',
      )

      return Response({
        'url': checkout_session.url,
        'id': checkout_session.id
      })

    except Exception as e:

      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
  permission_classes = [AllowAny]

  def post(self, request):
    print(">>> ATTENZIONE: IL WEBHOOK È STATO TOCCATO! <<<")
    print("--- WEBHOOK: Chiamata POST ricevuta da Stripe ---")
    payload = request.body
    print(f">>> PAYLOAD RICEVUTO: {payload[:50]}...")
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    print(f">>> SECRET USATO: {endpoint_secret[:10]}")

    try:
      event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
      print(f">>> EVENTO VALIDATO: {event['type']}")
    except Exception as e:
      print(f">>> ERRORE VALIDAZIONE FIRMA: {e}")
      return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed': #'payment_intent.succeeded':
      intent = event['data']['object']
      self.conferma_pagamento(intent)

    return HttpResponse(status=200)

  def conferma_pagamento(self, session):
  
    # Recuperiamo i metadata e l'importo corretto dalla Sessione
    metadata = session.get('metadata', {})
    
    print(f"--- DEBUG WEBHOOK: Dati Sessione: {session.get('id')} ---")
    print(f"Metadata estratti: {metadata}")

    customer_id = metadata.get('customer_id')
    tipo = metadata.get('type')
    
    # 1. Calcolo importo corretto per Checkout Session
    amount_total = session.get('amount_total', 0)
    importo = Decimal(amount_total) / 100

    if not customer_id:
        print("ATTENZIONE: customer_id assente. Se stai usando 'stripe trigger', è normale.")
        return

    try:
        # 2. Recupero Wallet
        wallet = Wallet.objects.get(user_id=customer_id)
        print(f"OK: Wallet trovato per utente {customer_id}")

        # 3. Gestione Ricarica Wallet
        if tipo == 'WALLET_RELOAD':
            wallet.balance += importo
            wallet.save()
            
            # Usiamo session.get('payment_intent') perché siamo in Checkout
            Transaction.objects.create(
                wallet=wallet, 
                amount=importo, 
                type='RELOAD', 
                stripe_intent_id=session.get('payment_intent')
            )
            print(f"SUCCESSO: Ricarica di {importo}€ salvata.")
        
        # 4. Gestione Pagamento Appuntamento
        elif tipo in ['APPOINTMENT', 'APPOINTMENT_PAY']:
            ids_str = metadata.get('appointment_ids', '')
            if ids_str:
                ids = ids_str.split(',')
                for app_id in ids:
                    if not app_id or app_id == 'None': continue
                    app = Appointment.objects.get(id=app_id)
                    # Aggiorniamo lo stato dell'appuntamento
                    app.amount_paid += importo 
                    app.payment_status = 'PAID'
                    app.save()
                    print(f"APPUNTAMENTO {app_id} SALDATO.")
            
            # Registriamo la transazione (senza influire sul saldo wallet)
            Transaction.objects.create(
                wallet=wallet, 
                amount=importo, 
                type='PAYMENT', 
                stripe_intent_id=session.get('payment_intent'), 
                affects_wallet_balance=False
            )

    except Exception as e:
        print(f"❌ DEBUG ERROR DURANTE SALVATAGGIO: {str(e)}")