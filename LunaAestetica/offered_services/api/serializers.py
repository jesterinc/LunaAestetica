# offered_services/api/serializers.py
from rest_framework import serializers
from offered_services.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    # Forziamo la conversione in stringa del prezzo per evitare errori di serializzazione Decimal
    price = serializers.DecimalField(max_digits=6, decimal_places=2, coerce_to_string=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'duration_minutes']