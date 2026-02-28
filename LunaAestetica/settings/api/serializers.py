# settings/api/serializers.py
from rest_framework import serializers
from settings.models import BusinessSettings

class BusinessSettingsSerializer(serializers.ModelSerializer):

  class Meta:
    model = BusinessSettings
    fields = ['start_time', 'end_time', 'minute_increment']

  def get_is_cancellable(self, obj):

    from settings.models import GeneralSettings

    gen = GeneralSettings.objects.first()
    limit_hours = gen.cancellation_limit_hours if gen else 0

    if limit_hours == 0:

      return self.get_is_future(obj)

    appt_datetime = timezone.make_aware(datetime.combine(obj.date, obj.start_time))
    return appt_datetime > (timezone.now() + timedelta(hours=limit_hours))