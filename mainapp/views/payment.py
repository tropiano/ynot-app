# payments/views.py

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from usermodel.models import User


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)  # Invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)  # Invalid signature

    # Handle the checkout.session.completed event
    # Handle the checkout.session.completed event

    if event["type"] == "checkout.session.completed":

        try:
            customer_details = event["data"]["object"]["customer_details"]
            email = customer_details["email"]
            # Update user and set it as paid
            User.objects.filter(email=email).update(is_paid=1)
        except Exception as e:
            return HttpResponse(status=400)  # Invalid signature

    return HttpResponse(status=200)
