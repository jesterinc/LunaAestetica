# days_hours/models.py
from django.db import models

class TimeSlot(models.Model):
  time = models.TimeField()
  active = models.BooleanField(default=True)

  class Meta:
    db_table = "time_slots"
    ordering = ['time']

  def __str__(self):
      
    return self.time.strftime("%H:%M")