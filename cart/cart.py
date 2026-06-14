from store.models import Product, Profile



# Algorthm for writing a successful cart session 
# 1. Create "Cart Logic" file in cart/cart.py
# Step 2: Register the context processor in project settings.py 
# This is to make sure the cart is available on every page so the navbar icon update. This is to tell django about the newly class app
# Step 3: Create the Context processor (cart/context_processors.py)
# In side the cart app/folder , create a context_processors.py that will feed the cart data into the HTML templates automatically
# Step 4: Set up the view and write the logic that will update the cart
# Step 5: Connect to the URLs In cart/urls.py
# Step 6: The Frontend AJAX(The "Trigger")
# Making Sure the Add to Cart button sends the data to this newly created url path
#### Cart Summary Page ####
# This is to pull those IDs out of the session and turn them back into real product objects so the user can see their total price, images, and descriptions.
# The Cart class is now storing data as {'product_id': {'price': '...', 'qty': ...}}, a way to loop through those IDs and fetch the actual Product objects from the database.
# Confirm by copying the session id from the inspect section of the page by clicking f12 or right click
# python manage.py shell in the terminal
# from django.contrib.sessions.models import Session
# session_k = Session.objects.get(pk='yoursessionkeyedqwjqwfqwefnqknc')
# session_k.get_decoded()
# Output:  'session_key': {'6': 1, '16': 1, '4': 1, '9': 1}}
# Converting this dicts to the actual data in the database

# Step 1:The "List Builder" (Update cart.py)
# A function that Django can use to loop through the cart items. 




class Cart:
    # Cart Initialization
    def __init__(self, request):
        # Store the current session and request object
        self.session = request.session
        self.request = request

        # Try to get the cart dictionary from the session
        cart = self.session.get('cart')

        # If no cart exists yet, initialize an empty one
        if not cart:
            cart = self.session['cart'] = {}

        # Make sure the cart is available everywhere in the class
        self.cart = cart

    # Create cart
    def add_to_cart(self, product, quantity, color="Default", size="Standard"):
        """
        Add a product variation combo to the session dictionary,
        and update backup data arrays on user profiles if authenticated.
        """
        product_id = str(product.id)
        product_qty = int(quantity)

        # Create a unique variant key (e.g. "5-Black-XL")
        variant_key = f"{product_id}-{color}-{size}"

        # Update or create the variant entry
        if variant_key in self.cart:
            self.cart[variant_key]['qty'] += product_qty
        else:
            self.cart[variant_key] = {
                'id': product_id,
                'qty': product_qty,
                'color': color,
                'size': size
            }

        # Mark the session as modified
        self.session.modified = True

        # Sync with user profile if logged in
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)

    # Add to database
    def add_to_database(self, product, quantity, color="Default", size="Standard"):
        
        #Add a product to the cart using its ID (passed directly),
        #and save the cart state to the user's Profile if logged in.
        
        product_id  = str(product)
        product_qty = int(quantity)

        # Create a unique variant key (e.g. "5-Black-XL")
        variant_key = f"{product_id}-{color}-{size}"

        # Update or create the variant entry
        if variant_key in self.cart:
            self.cart[variant_key]['qty'] += product_qty
        else:
            self.cart[variant_key] = {
                'id': product_id,
                'qty': product_qty,
                'color': color,
                'size': size
            }

        self.session.modified = True

        # If user is logged in, also save cart snapshot to Profile
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)        



    # Length or total numbers of items in the cart
    def __len__(self):
        """
        Return the total number of items in the cart (sum of quantities).
        """
        return sum(item['qty'] for item in self.cart.values())

    #Products in the cart.
    def get_products(self):
        """
        Return all Product objects currently in the cart.
        """
        product_ids = [item['id'] for item in self.cart.values()]
        product_values = Product.objects.filter(id__in=product_ids)
        return product_values

    # Dictionary of he cart items
    def get_quantities(self):
        """
        Return the raw dictionary of cart items.
        """
        return self.cart

    def update(self, product_id, quantity, color="Default", size="Standard"):
        """
        Update the quantity of a specific product variant in the cart.
        """
        product_id = str(product_id)  # keep as string
        variant_key = f"{product_id}-{color}-{size}"
        product_qty = int(quantity)

        if variant_key in self.cart:
            self.cart[variant_key]['qty'] = product_qty

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)


    def delete(self, product_id, color="Default", size="Standard"):
        """
        Remove a product variant completely from the cart.
        """
        product_id = str(product_id)
        variant_key = f"{product_id}-{color}-{size}"

        if variant_key in self.cart:
            del self.cart[variant_key]

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_convert = str(self.cart).replace("'", "\"")
            current_user.update(old_cart=cart_convert)
            

    # Total price of the items in the cart
    def cart_total(self):
        """
        Calculate the total price of all items in the cart.
        """
    
        total = 0
        for item in self.cart.values():
            product = Product.objects.get(id=item['id'])
            if product.is_sales:
                total += product.sale_price * item['qty']
            else:
                total += product.price * item['qty']
        return total

    # After placing order delete the cart
    def clear(self):
        """
        Empty the entire cart.
        """
        self.session['cart'] = {}
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            current_user.update(old_cart="{}")













 