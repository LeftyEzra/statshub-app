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
    # Initialize the cart object from cart.py using the current request session
    cart = Cart(request)
    
    # Check if the incoming request is an AJAX POST request with the action 'post'
    if request.POST.get('action') == 'post':
        
        # Capture the product ID and quantity from the AJAX data and convert them to integers
        product_id = request.POST.get('product_id')
        product_qty = int(request.POST.get('product_qty'))

        # --- THE UPDATE: Grab color and size from AJAX ---
        product_colors = request.POST.get("product_color", "Default")
        product_sizes = request.POST.get("product_size", "Standard")
        print("product color")
        print(product_colors)

        # Call the update method in the Cart class to save the new quantity to the session
        cart.update(product_id=product_id, quantity=product_qty, color=product_colors, size=product_sizes)

        # Get the new total count of items in the cart to update the navbar icon
        cart_quantity = cart.__len__()
        
        # Return a JSON response containing the new quantity back to the JavaScript
        response = JsonResponse({'qty': cart_quantity})
        
        return response

     

# Delete cart
def delete_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = request.POST.get("product_id")
        product_color = request.POST.get("product_color", "Default")
        product_size = request.POST.get("product_size", "Standard")

        cart.delete(product_id=product_id, color=product_color, size=product_size)

        response = JsonResponse({'product': product_id})
        messages.success(request, "Product Removed Successfully...")
        return response



def checkout(request):
    return render(request, 'checkout.html')







