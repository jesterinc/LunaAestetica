# meets/models.py
from django.db import models
from offered_services.models import Service

class Appointment(models.Model):
  customer = models.ForeignKey('login.Users', on_delete=models.CASCADE)
  services = models.ManyToManyField(Service)
  date = models.DateField()
  start_time = models.TimeField() # L'orario scelto dall'utente
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = "appointments"