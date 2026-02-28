#offered_sercices/api/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta, time
import traceback

from offered_services.models import Service, OpeningHour
from offered_services.api.serializers import ServiceSerializer
from login.models import Users

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(active=True)
    serializer_class = ServiceSerializer

    @action(detail=False, methods=['get'])
    def date_disponibili(self, request):
        # Import locale per evitare importazioni circolari
        from meets.models import Appointment
        try:
            durata_richiesta = int(request.query_params.get('durata', 60))
            oggi = datetime.now().date()
            regole_apertura = OpeningHour.objects.all()
            date_finali = []

            for i in range(60):
                data_esaminata = oggi + timedelta(days=i)
                giorno_settimana = data_esaminata.weekday()
                
                fasce_giorno = regole_apertura.filter(
                    Q(day_of_week=giorno_settimana),
                    Q(date_start__lte=data_esaminata) | Q(date_start__isnull=True),
                    Q(date_end__gte=data_esaminata) | Q(date_end__isnull=True)
                )
                
                if not fasce_giorno.exists():
                    continue

                impegni = Appointment.objects.filter(date=data_esaminata)
                black_list = []
                for app in impegni:
                    # CORRETTO: data_esaminata invece di data_obj
                    inizio_impegno = datetime.combine(data_esaminata, app.start_time)
                    durata_app = sum(s.duration_minutes for s in app.services.all())
                    fine_impegno = inizio_impegno + timedelta(minutes=durata_app)
                    black_list.append((inizio_impegno, fine_impegno))

                trovato_buco = False
                passo = 15
                
                for fascia in fasce_giorno:
                    corrente = datetime.combine(data_esaminata, fascia.start_hour)
                    fine_fascia = datetime.combine(data_esaminata, fascia.end_hour)
                        
                    while corrente + timedelta(minutes=durata_richiesta) <= fine_fascia:
                        slot_inizio = corrente
                        slot_fine = corrente + timedelta(minutes=durata_richiesta)
                        
                        sovrapposto = False
                        for b_inizio, b_fine in black_list:
                            if slot_inizio < b_fine and slot_fine > b_inizio:
                                sovrapposto = True
                                break
                        
                        if not sovrapposto:
                            trovato_buco = True
                            break
                        
                        corrente += timedelta(minutes=passo)
                    
                    if trovato_buco: 
                        break
                
                if trovato_buco:
                    date_finali.append(data_esaminata.strftime('%Y-%m-%d'))

            return Response(date_finali)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def orari_disponibili(self, request):
        from meets.models import Appointment
        try:
            data_str = request.query_params.get('data')
            durata_totale = int(request.query_params.get('durata', 30))

            if not data_str:
                return Response({"error": "Data mancante"}, status=400)

            data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            giorno_settimana = data_obj.weekday()

            fasce_query = OpeningHour.objects.filter(
                Q(day_of_week=giorno_settimana),
                Q(date_start__lte=data_obj) | Q(date_start__isnull=True),
                Q(date_end__gte=data_obj) | Q(date_end__isnull=True)
            )

            impegni = Appointment.objects.filter(date=data_obj)
            black_list = []
            for app in impegni:
                inizio_impegno = datetime.combine(data_obj, app.start_time)
                durata_app = sum(s.duration_minutes for s in app.services.all())
                fine_impegno = inizio_impegno + timedelta(minutes=durata_app)
                black_list.append((inizio_impegno, fine_impegno))

            orari_risultato = []
            passo_minuti = 15

            for fascia in fasce_query:
                corrente = datetime.combine(data_obj, fascia.start_hour)
                fine_fascia = datetime.combine(data_obj, fascia.end_hour)

                while corrente + timedelta(minutes=durata_totale) <= fine_fascia:
                    slot_inizio = corrente
                    slot_fine = corrente + timedelta(minutes=durata_totale)
                    
                    sovrapposto = False
                    for b_inizio, b_fine in black_list:
                        if slot_inizio < b_fine and slot_fine > b_inizio:
                            sovrapposto = True
                            break
                    
                    if not sovrapposto:
                        orari_risultato.append({
                            "ora": slot_inizio.strftime('%H:%M'),
                            "label": slot_inizio.strftime('%H:%M')
                        })

                    corrente += timedelta(minutes=passo_minuti)

            return Response(orari_risultato)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def prenota(self, request):
        from meets.models import Appointment
        try:
            service_ids = request.data.get('service_ids')
            data_prenotazione = request.data.get('date')
            ora_inizio = request.data.get('start_time')
            
            if not request.user.is_authenticated:
                return Response({"error": "Autenticazione richiesta"}, status=401)
            
            customer = Users.objects.get(email=request.user.email)

            if not all([service_ids, data_prenotazione, ora_inizio]):
                return Response({"error": "Dati incompleti"}, status=400)

            nuovo_appuntamento = Appointment.objects.create(
                customer=customer,
                date=data_prenotazione,
                start_time=ora_inizio
            )

            servizi = Service.objects.filter(id__in=service_ids)
            nuovo_appuntamento.services.set(servizi)

            return Response({"status": "success", "id": nuovo_appuntamento.id}, status=201)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)