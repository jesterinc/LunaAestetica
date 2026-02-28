#offered_services/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meets.api.views import AppointmentViewSet

router = DefaultRouter()
router.register(r'prenotazioni', AppointmentViewSet, basename='prenotazioni')

urlpatterns = [
    path('', include(router.urls)),
]