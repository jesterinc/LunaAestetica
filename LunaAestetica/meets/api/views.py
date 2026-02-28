# meets/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.utils import timezone

from settings.models import BusinessSettings, GeneralSettings

from meets.models import Appointment
from meets.api.serializers import AppointmentSerializer
from offered_services.models import Service

from datetime import datetime, timedelta
import datetime as dt_module

class AppointmentViewSet(viewsets.ModelViewSet):
  queryset = Appointment.objects.all()
  serializer_class = AppointmentSerializer

  def get_permissions(self):

    if self.action in ['me', 'create', 'salva_prenotazione']:

      return [IsAuthenticated()]

    return [IsAuthenticated()]

  def get_queryset(self):
  
    return Appointment.objects.filter(customer=self.request.user).order_by('-date')

  def perform_create(self, serializer):
  
    serializer.save(customer=self.request.user)

  @action(detail=False, methods=['get'], url_path='me')
  def me(self, request):
    """Endpoint: api/v1/meets/appointments/me/"""
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)

  @action(detail=True, methods=['post'])
  def cancel(self, request, pk=None):

    appointment = self.get_object()
    if not appointment.is_cancellable:

      return Response(
        {"detail": "Non è più possibile annullare questo appuntamento."},
        status=status.HTTP_400_BAD_REQUEST
      )

    appointment.status = 'CANC'
    appointment.save()
    return Response({
      'status': 'success',
      'message': 'Prenotazione annullata correttamente'
    })


class CustomerAppointmentViewSet(viewsets.ReadOnlyModelViewSet):
  permission_classes = [IsAuthenticated]
  serializer_class = AppointmentSerializer

  def get_queryset(self):

    return Appointment.objects.filter(customer=self.request.user).order_by('-date', '-start_time')



