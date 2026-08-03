from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse # Cart view
from django.contrib import messages
from store.models import Product
from .cart import Cart
# Create your views here.


# Create Cart
def add_to_cart(request):
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get("product_id"))
        product_qty = int(request.POST.get("product_qty"))
        
        # --- FIXED & UNCOMMENTED ---
        product_colors = request.POST.get("product_color", "Default")
        product_sizes = request.POST.get("product_size", "Standard")

        product = get_object_or_404(Product, id=product_id)

        # Passing the extracted strings over to the Class backend handler
        cart.add_to_cart(
            product=product, 
            quantity=product_qty, 
            color=product_colors, 
            size=product_sizes
        )

        cart_quantity = cart.__len__()

        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, ("Product Added To Cart "))
        return response

# Cart Details


def cart_summary(request):
    cart = Cart(request)
    quantities = cart.get_quantities()   # full dicts with id, qty, color, size

    cart_items = []
    grand_total = 0

    for key, item in quantities.items():
        product = Product.objects.get(id=item['id'])

        # Calculate subtotal
        if product.is_sales:
            subtotal = product.sales_price * item['qty']
            price = product.sales_price
        else:
            subtotal = product.price * item['qty']
            price = product.price

        grand_total += subtotal

        cart_items.append({
            'id': product.slug,
            'name': product.name,
            'image': product.image.url,
            'price': product.price,
            'sale_price': product.sales_price,
            'is_sales': product.is_sales,
            'qty': item['qty'],
            'color': item['color'],
            'size': item['size'],
            'subtotal': subtotal,
        })

    return render(request, "shopping-cart.html", {
        "cart_items": cart_items,
        "grand_totals": grand_total
    })


# Update cart
def update_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')
        product_qty = int(request.POST.get('product_qty'))

        product_colors = request.POST.get("product_color", "Default")
        product_sizes = request.POST.get("product_size", "Standard")

        cart.update(product_id=product_id, quantity=product_qty, color=product_colors, size=product_sizes)

        cart_quantity = cart.__len__()
        return JsonResponse({'qty': cart_quantity})

# Delete cart
def delete_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get("product_id")
        product_color = request.POST.get("product_color", "D")
        product_size = request.POST.get("product_size", "STD")

        cart.delete(product_id=product_id, color=product_color, size=product_size)

        # Return the new total item count so navbar/dropdown updates correctly
        cart_quantity = cart.__len__()
        
        return JsonResponse({'qty': cart_quantity, 'product': product_id})



def checkout(request):
    return render(request, 'checkout.html')







