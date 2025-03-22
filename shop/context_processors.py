from .models import Cart

def cart_context(request):
    cart_count = 0
    
    # Get cart based on user or session
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_id=session_key).first()
            if cart:
                cart_count = cart.items.count()
    
    return {'cart_count': cart_count}