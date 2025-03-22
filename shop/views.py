from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def shop_view(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/shop.html', context)

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    # Check if we're receiving JSON data (for AJAX requests)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        quantity = data.get('quantity', 1)
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    # Check if product is in stock
    if product.quantity < quantity:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Not enough items in stock'}, status=400)
        return redirect('shop')
    
    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # If product already exists in cart, update quantity
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = cart.items.count()
        return JsonResponse({'success': True, 'cart_total': cart_count})
    
    return redirect('cart')

def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})

def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'remove':
            cart_item.delete()
        elif action == 'update':
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0 and quantity <= cart_item.product.quantity:
                cart_item.quantity = quantity
                cart_item.save()
    
    return redirect('cart_view')

def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        return redirect('shop_view')
    
    context = {
        'cart': cart,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'shop/checkout.html', context)

@csrf_exempt
def create_payment_intent(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))
        name = data.get('name', '')
        email = data.get('email', '')
        address = data.get('address', '')
        
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Create a payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'name': name,
                'email': email,
                'address': address
            }
        )
        
        return JsonResponse({
            'client_secret': intent.client_secret
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent', '')
    
    if not payment_intent_id:
        return redirect('shop_view')
    
    try:
        # Verify the payment intent with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            # Get the cart
            cart = get_or_create_cart(request)
            
            # Create an order record
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=payment_intent.metadata.get('name', ''),
                email=payment_intent.metadata.get('email', ''),
                address=payment_intent.metadata.get('address', ''),
                amount=payment_intent.amount / 100,  # Convert from cents back to dollars
                payment_intent_id=payment_intent_id,
                payment_status='completed'
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=float(cart_item.product.price),
                    quantity=cart_item.quantity
                )
                
                # Update product inventory
                product = cart_item.product
                product.quantity -= cart_item.quantity
                product.save()
            
            # Clear the cart
            cart.items.all().delete()
            
            return render(request, 'shop/payment_success.html', {
                'payment_intent': payment_intent,
                'order': order
            })
        else:
            return redirect('checkout')
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        return redirect('checkout')

def payment_cancel(request):
    return render(request, 'shop/payment_cancel.html')