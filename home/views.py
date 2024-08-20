from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from demo.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY, STRIPE_WEBHOOK_SECRET

stripe.api_key = STRIPE_SECRET_KEY


# Create your views here.

def home(request):
    return render(request, "index.html", {'STRIPE_PUBLIC_KEY': STRIPE_PUBLIC_KEY})

def create_checkout(request):
    YOUR_DOMAIN = "https://thetoolclub.com"
    cancel_url = '/'
    success_url = '/'
    data = json.loads(request.body)
    price = data.get('price')
    plan_name = data.get('planName')

    checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan_name,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                        'unit_amount': price * 100,
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "unit_amount": price
            },
            mode='payment',
            success_url=YOUR_DOMAIN + success_url,
            cancel_url=YOUR_DOMAIN + cancel_url,
        )
    return JsonResponse({
        'id': checkout_session.id
    })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        return JsonResponse("Succesful!")

    # Passed signature verification
    return HttpResponse(status=200)
