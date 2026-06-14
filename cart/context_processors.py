
from .cart import Cart





def cart(request):
    cart_obj = Cart(request)
    
    # We return the exact variable names in HTML loop is using
    return {
        'cart': cart_obj,
        'cart_products': cart_obj.get_products(), # Matches the {% for product in cart_products %}
        'totals' : cart_obj.cart_total(),
    }  