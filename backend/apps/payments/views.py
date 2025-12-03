from django.conf import settings
from django.http import HttpRequest, HttpResponse

import stripe
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CheckoutView(APIView):
    def post(self, request: HttpRequest) -> Response:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # NOTE: minimal placeholder PaymentIntent
        intent = stripe.PaymentIntent.create(amount=1000, currency="usd")
        return Response({"client_secret": intent["client_secret"]})


class StripeWebhookView(APIView):
    def post(self, request: HttpRequest) -> Response:
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=endpoint_secret
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # Handle a subset of events
        if event["type"] in {"payment_intent.succeeded", "checkout.session.completed"}:
            # Reconciliation can be implemented here by looking up Invoice by metadata
            pass
        return Response({"received": True}, status=status.HTTP_200_OK)
