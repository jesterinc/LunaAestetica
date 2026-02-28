# settings/models.py
from django.db import models

class BusinessSettings(models.Model):
  start_time = models.TimeField(default="09:00") # Apertura
  end_time = models.TimeField(default="18:00")   # Chiusura
  minute_increment = models.PositiveIntegerField(default=15) # L'incremento di cui parlavi (5, 10, 15 min)

  class Meta:
    db_table = "business_settings"
    verbose_name = "Impostazioni Aziendali"