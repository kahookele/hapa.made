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
        
        # Create a pending booking record
        booking = Booking.objects.create(
            workshop=workshop,
            name=name,
            email=email,
            phone=phone,
            payment_status='pending'  # Set initial status as pending
        )
        
        # Store the Stripe session ID in the booking
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
                    'booking_id': booking.id,
                    'name': name,
                    'email': email,
                    'phone': phone,
                },
                success_url=request.build_absolute_uri('/booking-success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/booking-cancel/'),
            )
            
            # Store Stripe session ID
            booking.stripe_session_id = session.id
            booking.save()
            
            return redirect(session.url)
        except Exception as e:
            # Delete the booking if Stripe fails
            booking.delete()
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
        booking_id = session.get('metadata', {}).get('booking_id')
        
        if booking_id:
            try:
                # Get the booking by ID
                booking = Booking.objects.get(id=booking_id)
                
                # Update payment status
                booking.payment_status = 'paid'
                booking.save()
                
                # Explicitly decrease the workshop's available seats
                workshop = booking.workshop
                workshop.seats_available = max(0, workshop.seats_available - 1)
                workshop.save()
                
                return HttpResponse(status=200)
            except Booking.DoesNotExist:
                pass  # Continue to legacy fallback method
        
        # Legacy fallback logic
        if workshop_id:
            try:
                # Find the workshop by ID
                workshop = Workshop.objects.get(id=workshop_id)
                
                # Create a booking record if it doesn't exist
                customer_email = session.get('customer_details', {}).get('email')
                if customer_email:
                    # Check if we already have a booking with this session ID
                    existing_booking = Booking.objects.filter(stripe_session_id=session.id).first()
                    if not existing_booking:
                        # Create a new booking
                        booking = Booking.objects.create(
                            workshop=workshop,
                            name=session.get('metadata', {}).get('name', 'Customer'),
                            email=customer_email,
                            phone=session.get('metadata', {}).get('phone', ''),
                            payment_status='paid',
                            stripe_session_id=session.id
                        )
                        
                        # Update available seats
                        workshop.seats_available = max(0, workshop.seats_available - 1)
                        workshop.save()
            except Workshop.DoesNotExist:
                # Workshop not found
                return HttpResponse(status=400)
            except Exception as e:
                # Other errors
                return HttpResponse(status=400)
                
    return HttpResponse(status=200)

def booking_success(request):
    # Get the session ID from the URL parameters
    session_id = request.GET.get('session_id')
    booking = None
    workshop = None
    
    if session_id:
        # If we have a session ID from Stripe, fetch the booking
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Retrieve the session data from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            booking_id = session.metadata.get('booking_id')
            
            if booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id)
                    workshop = booking.workshop
                    
                    # Ensure payment status is updated
                    if booking.payment_status != 'paid':
                        booking.payment_status = 'paid'
                        booking.save()
                        
                        # Decrease available seats if not already done
                        if workshop.seats_available > 0:
                            workshop.seats_available -= 1
                            workshop.save()
                except Booking.DoesNotExist:
                    messages.warning(request, "Your booking information could not be found.")
            # ... existing fallback code ...
        except Exception as e:
            messages.error(request, f"Error retrieving booking information: {str(e)}")
    
    # Render the success page (with or without booking details)
    return render(request, 'workshop/booking_success.html', {
        'booking': booking,
        'workshop': workshop
    })

def booking_cancel(request):
    messages.error(request, "Booking cancelled.")
    return redirect('workshop_list')