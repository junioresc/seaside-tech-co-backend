from django.urls import path

from .views import CheckoutView, StripeWebhookView

urlpatterns = [
    path("cart/checkout/", CheckoutView.as_view(), name="checkout"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
