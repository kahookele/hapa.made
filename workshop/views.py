from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from .models import Workshop, Booking
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def workshop_list(request):
    workshops = Workshop.objects.all()
    return render(request, 'workshop/workshop_list.html', {'workshops': workshops})

def book_workshop(request, workshop_id):
    # Get the workshop and check availability
    workshop = get_object_or_404(Workshop, id=workshop_id)
    if workshop.seats_available <= 0:
        messages.error(request, f"'{workshop.title}' is fully booked. No more spots available.")
        return redirect('workshop_list')
    
    # Create a Stripe Checkout Session without creating a booking record now
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': workshop.title},
                'unit_amount': int(workshop.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://yourdomain.com/workshop/booking-success/?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://yourdomain.com/workshop/booking-cancel/',
        metadata={'workshop_id': workshop.id}
    )
    
    return redirect(session.url)

def booking_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No session ID provided.")
        return redirect('workshop_list')
    
    # Retrieve the Stripe Checkout Session
    session = stripe.checkout.Session.retrieve(session_id)
    
    if session.payment_status == 'paid':
        workshop_id = session.metadata.get('workshop_id')
        workshop = get_object_or_404(Workshop, id=workshop_id)
        
        # Extract customer details from Stripe (if available)
        customer_details = session.get('customer_details', {}) or {}
        name = customer_details.get('name', 'N/A')
        email = customer_details.get('email', '')
        
        # Create the booking record only after payment is successful
        booking = Booking.objects.create(
            workshop=workshop,
            name=name,
            email=email,
            phone='',  # Update if you have phone info from Stripe or elsewhere
            payment_status='paid'
        )
        
        # Decrease the available seats
        workshop.seats_available -= 1
        workshop.save()
        
        messages.success(request, "Your booking and payment were successful!")
        return redirect('workshop_list')
    else:
        messages.error(request, "Payment was not successful.")
        return redirect('workshop_list')

def booking_cancel(request):
    messages.error(request, "Booking cancelled.")
    return redirect('workshop_list')