# meets/api/serializers.py
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from meets.models import Appointment
from offered_services.api.serializers import ServiceSerializer 

class AppointmentSerializer(serializers.ModelSerializer):
    # Definiamo esplicitamente tutti i campi calcolati
    is_future = serializers.ReadOnlyField()
    is_cancellable = serializers.ReadOnlyField()
    is_cancelled = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    service_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    total_duration = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'date', 'start_time', 'services', 'service_ids', 
            'is_cancellable', 'is_future', 'is_cancelled', 
            'total_price', 'total_duration', 'status_display'
        ]

    def get_full_datetime(self, obj):
        """Unifica data e ora rendendole 'aware' (sicure per il confronto)"""
        if not obj.date or not obj.start_time:
            return timezone.now()
        naive_dt = datetime.combine(obj.date, obj.start_time)
        return timezone.make_aware(naive_dt, timezone.get_current_timezone())

    def get_is_future(self, obj):
        """Ritorna True se l'appuntamento deve ancora avvenire"""
        return self.get_full_datetime(obj) > timezone.now()

    def get_is_cancelled(self, obj):
        
        return obj.status == 'CANC'
    
    def get_is_cancellable(self, obj):
        """Cancellabile se non è già CANC e mancano più di 24h"""
        if hasattr(obj, 'status') and obj.status == 'CANC':
            return False
        
        now = timezone.now()
        app_dt = self.get_full_datetime(obj)
        # La riga seguente ora è indentata correttamente con 8 spazi totali
        return app_dt > (now + timedelta(hours=24))

    def get_total_price(self, obj):
        """Somma il prezzo di tutti i servizi associati"""
        return sum(s.price for s in obj.services.all())

    def get_total_duration(self, obj):
        """Somma la durata di tutti i servizi associati"""
        return sum(s.duration_minutes for s in obj.services.all())

    def create(self, validated_data):
        """Gestisce la creazione dell'appuntamento con i relativi servizi"""
        service_ids = validated_data.pop('service_ids')
        customer = self.context['request'].user
        appointment = Appointment.objects.create(customer=customer, **validated_data)
        appointment.services.set(service_ids)
        return appointment