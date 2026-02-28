# settings/api/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from settings.models import BusinessSettings, GeneralSettings

class ClientConfigurationView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):

    biz = BusinessSettings.objects.first()
    gen = GeneralSettings.objects.first()

    return Response({
      "cancellation_limit_hours": gen.cancellation_limit_hours if gen else 0,
      "modification_limit_hours": gen.modification_limit_hours if gen else 0,
      "show_prices": gen.show_prices_to_customer if gen else False,
      "minute_increment": biz.minute_increment if biz else 15,
      "server_time": timezone.now() 
    })

    