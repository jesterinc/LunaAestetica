# offered_services/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from offered_services.api.views import ServiceViewSet

router = DefaultRouter()
router.register(r'servizi', ServiceViewSet, basename='servizi')

urlpatterns = [
    path('servizi/date_disponibili/', ServiceViewSet.as_view({'get': 'date_disponibili'}), name='servizi-date-disponibili'),
    path('servizi/orari_disponibili/', ServiceViewSet.as_view({'get': 'orari_disponibili'}), name='servizi-orari-disponibili'),
    path('', include(router.urls)),
]