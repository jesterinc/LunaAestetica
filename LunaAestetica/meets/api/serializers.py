# meets/api/serializers.py
from rest_framework import serializers
from meets.models import Appointment
from offered_services.models import Service

class AppointmentSerializer(serializers.ModelSerializer):
  service_ids = serializers.ListField(child=serializers.IntegerField(),write_only=True)

  class Meta:
    model = Appointment
    fields = ['id', 'date', 'start_time', 'service_ids']

  def create(self, validated_data):
  
    service_ids = validated_data.pop('service_ids')
    request = self.context.get('request')
  
    if not request or not request.user.is_authenticated:
  
      raise serializers.ValidationError("Utente non autenticato.")
          
    customer = request.user
    appointment = Appointment.objects.create(customer=customer,**validated_data)
    appointment.services.set(service_ids)

    return appointment
