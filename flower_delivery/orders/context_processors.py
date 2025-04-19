# orders/context_processors.py
from .models import Cart

def cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        return {'cart_items': cart_items, 'cart_total': sum(item.product.price * item.quantity for item in cart_items)}
    return {}