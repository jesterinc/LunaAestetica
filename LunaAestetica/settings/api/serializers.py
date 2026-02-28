# settings/api/serializers.py
from rest_framework import serializers
from settings.models import BusinessSettings

class BusinessSettingsSerializer(serializers.ModelSerializer):

  class Meta:
    model = BusinessSettings
    fields = ['start_time', 'end_time', 'minute_increment']