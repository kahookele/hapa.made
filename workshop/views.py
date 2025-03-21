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
    workshop = get_object_or_404(Workshop, id=workshop_id)
    if workshop.seats_available <= 0:
        messages.error(request, "No more spots available.")
        return redirect('workshop_list')

    # Replace with your actual Stripe Payment Link
    stripe_payment_link = "https://buy.stripe.com/test_aEU7tP6Kp9cn5ZSfYY"
    return redirect(stripe_payment_link)

def booking_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        messages.error(request, "No session ID provided.")
        return redirect('workshop_list')
    
    session = stripe.checkout.Session.retrieve(session_id)
    
    if session.payment_status == 'paid':
        workshop_id = session.metadata.get('workshop_id')
        workshop = get_object_or_404(Workshop, id=workshop_id)
        
        # Retrieve metadata
        name = session.metadata.get('name', 'N/A')
        email = session.metadata.get('email', '')
        phone = session.metadata.get('phone', '')

        # Create the booking record
        booking = Booking.objects.create(
            workshop=workshop,
            name=name,
            email=email,
            phone=phone,
            payment_status='paid'
        )
        
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