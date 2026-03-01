# payments/api/views.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

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
      amount_to_charge = Decimal('0.00')
      metadata = {
        'customer_id': request.user.id,
        'type': data.get('type') 
      }
      if data.get('type') == 'APPOINTMENT_PAY':
        appointment_ids = data.get('appointment_ids', [])
        appointments = Appointment.objects.filter(id__in=appointment_ids, customer=request.user)
        total = sum(app.remaining_amount for app in appointments)
        amount_to_charge = total
        metadata['appointment_ids'] = ",".join(map(str, appointment_ids))
      elif data.get('type') == 'WALLET_RELOAD':
        amount_to_charge = Decimal(str(data.get('amount')))
        metadata['is_reload'] = 'true'

      intent = stripe.PaymentIntent.create(
        amount=int(amount_to_charge * 100),
        currency='eur',
        metadata=metadata,
        automatic_payment_methods={'enabled': True},
      )
      return Response({
        'clientSecret': intent.client_secret, 
        'amount': amount_to_charge
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

    if event['type'] == 'payment_intent.succeeded':
      intent = event['data']['object']
      self.conferma_pagamento(intent)

    return HttpResponse(status=200)

  def conferma_pagamento(self, intent):
    metadata = intent.get('metadata', {})
    print(f"--- DEBUG WEBHOOK: Dati evento: {intent.get('id')} ---")
    print(f"Metadata estratti: {metadata}")
    
    customer_id = metadata.get('customer_id')
    tipo = metadata.get('type')

    if not customer_id:
      print("ATTENZIONE: customer_id assente. Se stai usando 'stripe trigger', è normale.")
      return

    try:
      importo = Decimal(intent['amount']) / 100
      wallet = Wallet.objects.get(user_id=customer_id)
      print(f"OK: Wallet trovato per utente {customer_id}")

      if tipo == 'WALLET_RELOAD':
        wallet.balance += importo
        wallet.save()
        Transaction.objects.create(wallet=wallet, amount=importo, type='RELOAD', stripe_intent_id=intent['id'])
        print(f"SUCCESSO: Ricarica di {importo}€ salvata.")
      
      elif tipo == 'APPOINTMENT_PAY':
        ids = metadata.get('appointment_ids', '').split(',')
        for app_id in ids:
          if not app_id: continue
          app = Appointment.objects.get(id=app_id)
          app.amount_paid += app.remaining_amount
          app.payment_status = 'PAID'
          app.save()
          print(f"APPUNTAMENTO {app_id} SALDATO.")
        Transaction.objects.create(wallet=wallet, amount=importo, type='PAYMENT', stripe_intent_id=intent['id'], affects_wallet_balance=False)

    except Exception as e:
      print(f"DEBUG ERROR: {e}")