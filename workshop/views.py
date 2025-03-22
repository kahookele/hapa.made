from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Workshop, Booking
import stripe

def workshop_list(request):
    workshops = Workshop.objects.all()
    context = {
        'workshops': workshops,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'workshop/workshop_list.html', context)

def book_workshop(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    if workshop.seats_available <= 0:
        messages.error(request, "No more spots available.")
        return redirect('workshop_list')
    
    if request.method == 'POST':
        # Collect form details
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': workshop.title,
                        },
                        'unit_amount': int(workshop.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                metadata={
                    'workshop_id': workshop.id,
                    'name': name,
                    'email': email,
                    'phone': phone,
                },
                success_url=request.build_absolute_uri('/booking-success/'),
                cancel_url=request.build_absolute_uri('/booking-cancel/'),
            )
            return redirect(session.url)
        except Exception as e:
            messages.error(request, "Checkout creation failed: " + str(e))
            return redirect('workshop_list')
    
    # For GET requests, redirect back to the workshops list
    messages.info(request, "Please complete your booking using the modal on the workshops page.")
    return redirect('workshop_list')

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
        
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extract metadata from the session to identify the booking
        workshop_id = session.get('metadata', {}).get('workshop_id')
        name = session.get('metadata', {}).get('name')
        email = session.get('metadata', {}).get('email')
        phone = session.get('metadata', {}).get('phone')
        
        if workshop_id and email:
            try:
                workshop = Workshop.objects.get(id=workshop_id)
                # Create booking record if it doesn't exist yet
                booking, created = Booking.objects.get_or_create(
                    workshop=workshop,
                    email=email,
                    defaults={
                        'name': name,
                        'phone': phone,
                        'payment_status': 'paid'
                    }
                )
                
                if created:
                    # Decrease available seats
                    workshop.seats_available -= 1
                    workshop.save()
            except Workshop.DoesNotExist:
                pass
    
    return HttpResponse(status=200)

def booking_success(request):
    messages.success(request, "Your booking and payment were successful!")
    return redirect('workshop_list')

def booking_cancel(request):
    messages.error(request, "Booking cancelled.")
    return redirect('workshop_list')