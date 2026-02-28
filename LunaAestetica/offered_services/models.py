# offered_services/models.py
from django.db import models
from django.conf import settings

class Service(models.Model):
  name = models.CharField(max_length=100)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  duration_minutes = models.PositiveIntegerField() # es. 45, 60, 90
  active = models.BooleanField(default=True)
  
  class Meta:
    db_table = "services"

  def __str__(self):
    
    return f"{self.name} ({self.duration_minutes} min)"


class OpeningHour(models.Model):
  
  day_of_week = models.IntegerField(choices=settings.DAY_CHOICES)
  date_start = models.DateField(null=True, blank=True)
  date_end = models.DateField(null=True, blank=True)
  start_hour = models.TimeField()
  end_hour = models.TimeField()

  class Meta:
    verbose_name = "Regola di Apertura"
    ordering = ['day_of_week', 'start_hour']

  def __str__(self):
  
    return f"{self.get_day_of_week_display()}: {self.start_hour}-{self.end_hour}"