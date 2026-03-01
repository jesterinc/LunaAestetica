from django.conf import settings
from django.db import models

class Wallet(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
  balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-updated_at']

  def __str__(self):
    
    return f"Wallet di {self.user.email} - Saldo: {self.balance}€"


class Transaction(models.Model):
  wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  type = models.CharField(max_length=10, choices=settings.WALLET_TRANSACTION_TYPES)
  external_reference = models.CharField(max_length=255, blank=True, null=True)     
  is_manual = models.BooleanField(default=False) # True if done by service offerer ie. refund by cash
  appointment = models.ForeignKey('meets.Appointment', null=True, blank=True, on_delete=models.SET_NULL,related_name='wallet_transactions')
  stripe_intent_id = models.CharField(max_length=255, blank=True, null=True)
  affects_wallet_balance = models.BooleanField(default=True, help_text="If False, transaction is only historicalaof a direct stripe payment")
  created_at = models.DateTimeField(auto_now_add=True)
  description = models.TextField(blank=True)
  note = models.TextField(blank=True)

  class Meta:
    ordering = ['-created_at']
