# meets/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

from decimal import Decimal

from offered_services.models import Service

class Appointment(models.Model):
  customer = models.ForeignKey('login.Users', on_delete=models.CASCADE)
  services = models.ManyToManyField(Service)
  date = models.DateField()  
  start_time = models.TimeField()
  status = models.CharField(max_length=4, choices=settings.STATUS_CHOICES, default='PEND')
  payment_status = models.CharField(max_length=10, choices=settings.PAYMENT_STATUS_CHOICES, default='UNPAID')
  amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = "appointments"

  @property
  def total_price(self):
    """Calcola il prezzo totale basato sui servizi correnti"""
    return sum(s.price for s in self.services.all())

  @property
  def remaining_amount(self):
    """Restituisce quanto manca da pagare"""
    return self.total_price - self.amount_paid

  @property
  def full_datetime(self):
    """Unify date and hour in one obiect aware of timezone"""
    if not self.date or not self.start_time:

      return timezone.now()

    naive_dt = datetime.combine(self.date, self.start_time)
    return timezone.make_aware(naive_dt, timezone.get_current_timezone())

  @property
  def is_cancellable(self):
    """Return true if time to meet is greater than 24 hours"""
    if self.status == 'CANC':

      return False
      
    limit = timezone.now() + timedelta(hours=24)
    return self.full_datetime > limit

  @property
  def is_future(self):
    """Return True if meet is in a future"""
    return self.full_datetime > timezone.now()