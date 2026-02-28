# meets/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from settings.models import BusinessSettings

from meets.models import Appointment
from meets.api.serializers import AppointmentSerializer
from offered_services.models import Service

from datetime import datetime, timedelta
import datetime as dt_module # Alias per evitare conflitti con la classe datetime

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
    def get_permissions(self):

      if self.action in ['create', 'salva_prenotazione']:

        return [IsAuthenticated()]

      return []

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
class AppointmentViewSet(viewsets.ModelViewSet):

  queryset = Appointment.objects.all()
  serializer_class = AppointmentSerializer

  @action(detail=False, methods=['get'])
  def date_disponibili(self, request):

    today = dt_module.date.today()
    date_valide = []
    
    for i in range(30):
      
      giorno = today + timedelta(days=i)
      
      if giorno.weekday() != 6:
      
        date_valide.append(giorno.strftime('%Y-%m-%d'))
    
    return Response(date_valide)

  @action(detail=False, methods=['get'])
  def orari_liberi(self, request):
  
    data_str = request.query_params.get('data')
    durata_richiesta = request.query_params.get('durata') # La durata totale del carrello (es. 105)

    if not data_str or not durata_richiesta:
  
      return Response({"error": "Data e durata obbligatori"}, status=400)

    try:

      durata_richiesta = int(durata_richiesta)
      config = BusinessSettings.objects.first()

      if not config:

        return Response({"error": "Configurazione mancante"}, status=500)

      data_selezionata = datetime.strptime(data_str, '%Y-%m-%d').date()
      esistenti = Appointment.objects.filter(date=data_selezionata).prefetch_related('services')
      orari_disponibili = []
      corrente = datetime.combine(data_selezionata, config.start_time)
      limite_fine = datetime.combine(data_selezionata, config.end_time)

      while corrente + timedelta(minutes=durata_richiesta) <= limite_fine:

        inizio_test = corrente
        fine_test = corrente + timedelta(minutes=durata_richiesta)
        sovrapposto = False
        
        for app in esistenti:

          durata_app_esistente = sum(s.duration_minutes for s in app.services.all())
          app_inizio = datetime.combine(data_selezionata, app.start_time)
          app_fine = app_inizio + timedelta(minutes=durata_app_esistente)
          
          if inizio_test < app_fine and fine_test > app_inizio:

            sovrapposto = True
            break
        
        if not sovrapposto:

          orari_disponibili.append({
            "id": inizio_test.strftime('%H%M'),
            "ora": inizio_test.strftime('%H:%M')
          })
        
        corrente += timedelta(minutes=config.minute_increment)

      return Response(orari_disponibili)

    except Exception as e:

      print(f"ERRORE SERVER: {str(e)}") # Vedi l'errore nel terminale
      return Response({"error": str(e)}, status=500)
"""
