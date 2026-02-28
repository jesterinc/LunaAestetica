# meets/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone  # <--- MANCAVA QUESTO
from datetime import datetime, timedelta # <--- E QUESTI PER I CALCOLI

from offered_services.models import Service

class Appointment(models.Model):
  customer = models.ForeignKey('login.Users', on_delete=models.CASCADE)
  services = models.ManyToManyField(Service)
  date = models.DateField()  
  start_time = models.TimeField()
  status = models.CharField(max_length=4, choices=settings.STATUS_CHOICES, default='PEND')
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = "appointments"

  @property
  def full_datetime(self):
    """Unifica data e ora in un oggetto consapevole del fuso orario"""
    if not self.date or not self.start_time:

      return timezone.now()

    naive_dt = datetime.combine(self.date, self.start_time)
    return timezone.make_aware(naive_dt, timezone.get_current_timezone())

  @property
  def is_cancellable(self):
    """Ritorna True se mancano più di 24 ore e non è già cancellato"""
    if self.status == 'CANC':

      return False
      
    limit = timezone.now() + timedelta(hours=24)
    return self.full_datetime > limit

  @property
  def is_future(self):
    """Ritorna True se l'appuntamento deve ancora avvenire"""
    return self.full_datetime > timezone.now()