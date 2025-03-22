from .models import Cart

def cart_count(request):
    cart_count = 0
    
    if request.user.is_authenticated:
        # Get cart for logged in user
        cart = Cart.objects.filter(user=request.user).first()
    else:
        # Get cart for anonymous user via session
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart = Cart.objects.filter(session_id=session_id).first()
    
    if cart:
        cart_count = sum(item.quantity for item in cart.items.all())
    
    return {'cart_count': cart_count}