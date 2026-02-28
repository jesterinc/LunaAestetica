# settings/api/urls.py
from django.urls import path
from settings.api.views import ClientConfigurationView

urlpatterns = [
    # Questo risponderà a: /api/v1/settings/client-config/
    path('client-config/', ClientConfigurationView.as_view(), name='client-config'),
]