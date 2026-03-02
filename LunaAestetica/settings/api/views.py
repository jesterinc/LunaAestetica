# settings/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone

from settings.models import BusinessSettings, GeneralSettings

class ClientConfigurationView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):

    biz = BusinessSettings.objects.first()
    gen = GeneralSettings.objects.first()

    return Response({
      "cancellation_limit_hours": gen.cancellation_limit_hours if gen else 0,
      "modification_limit_hours": gen.modification_limit_hours if gen else 0,
      "minute_increment": biz.minute_increment if biz else 15,
      "show_prices": gen.show_prices_to_customer if gen else False,
      "server_time": timezone.now(),
      "payment_policy": gen.payment_policy if gen else 'NONE',
      "payment_amount": gen.payment_amount if gen else 0,
      "wallet_enabled": gen.wallet_enabled if gen else True,
    })

    