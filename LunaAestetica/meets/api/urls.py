# meets/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meets.api.views import AppointmentViewSet 

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]   