# payments/api/serializers.py
from rest_framework import serializers
from payments.models import Wallet, Transaction
from meets.api.serializers import AppointmentSerializer

class TransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    appointment_id = serializers.PrimaryKeyRelatedField(source='appointment', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
          'id', 'amount', 'type', 'type_display', 'appointment_id',
          'stripe_intent_id', 'affects_wallet_balance','is_manual','created_at', 'note'
        ]

class WalletSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()
    
    class Meta:
      model = Wallet
      fields = ['balance', 'updated_at', 'transactions']

    def get_transactions(self, obj):
    
      queryset = obj.transactions.all()[:10]
      return TransactionSerializer(queryset, many=True).data