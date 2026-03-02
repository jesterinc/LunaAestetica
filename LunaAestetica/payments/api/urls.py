# payments/api/urls.py
from django.urls import path
from payments.api.views import * #StripeWebhookView 

urlpatterns = [
  path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
  path('create-checkout-session/', StripeCheckoutView.as_view(), name='stripe-checkout'),
  path('wallet/', WalletViewSet.as_view({'get': 'list'}), name='wallet-detail'),
]