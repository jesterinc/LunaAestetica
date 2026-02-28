# login/urls.py
from django.urls import path
from login.api.views import LoginView, PasswordRecoverView, RegisterView 

urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),
    path('register/', RegisterView.as_view(), name='api-register'),
    path('password-reset/', PasswordRecoverView.as_view(), name='api-password-reset'),
]