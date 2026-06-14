from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse # Cart view
from django.contrib import messages
from store.models import Product, Profile
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required # For django locking App
from team.views import is_superuser
from team.models import Contact, NewsletterSubscriber
from services.models import FitnessRegistration, KitchenBooking, CaregiverRequest, BasketballCoachingRegistration
from cart.cart import Cart # Importing the Cart  
from payment.forms import ShippingForm
from payment.models import ShippingAddress, Order, OrderItem
from django.conf import settings 

from django.db.models import Sum, F, Value, IntegerField,ExpressionWrapper, FloatField
from django.db.models.functions import Cast # Casting string to integer
from datetime import datetime, timedelta # Module to represent the fifference between two dates
from django.utils.timezone import now
from django .utils import timezone

#PDF HTML Download
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

from calendar import HTMLCalendar
import plotly.graph_objects as go
from operator import itemgetter
from datetime import date
import datetime
import pandas as pd
import plotly  # This is needed for PlotlyJSONEncoder
import json


# Create your views here.


def checkout(request):
    current_user_profile = None 
    shipping_form = None

    cart = Cart(request)
    quantities = cart.get_quantities() # Full dictionary: {"5-Red-M": {"id": "5", "qty": 2, "color": "Red", "size": "M"}}
    
    #  SAFELY CALCULATING THE DYNAMIC GRAND TOTAL WITH VARIANT VALUES
    grand_total = 0
    cart_items_processed = []

    for key, item in quantities.items():
        try:
            product = Product.objects.get(id=int(item['id']))
            qty = int(item['qty'])
            price = product.sale_price if product.is_sales else product.price
            subtotal = price * qty
            grand_total += subtotal

            # Save processed data array to pass to template smoothly
            cart_items_processed.append({
                'product': product,
                'id': product.id,
                'name': product.name,
                'image': product.image.url if product.image else '',
                'price': product.price,
                'sale_price': product.sale_price,
                'is_sales': product.is_sales,
                'qty': qty,
                'color': item.get('color', 'Default'),
                'size': item.get('size', 'Standard'),
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            continue

    # ==========================================
    # REGISTERED USER WORKFLOW
    # ==========================================
    if request.user.is_authenticated:
        current_user_profile = Profile.objects.filter(user=request.user).first()
        shipping_user = ShippingAddress.objects.filter(user=request.user).order_by('-id').first()
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if request.method == 'POST':
            is_same_address = request.POST.get('input-checkbox-1') 

            if is_same_address and current_user_profile:
                full_name = f"{request.user.first_name} {request.user.last_name}"
                email = request.user.email
                shipping_address = f"{current_user_profile.address1}, {current_user_profile.state}, {current_user_profile.country}"
                phone = current_user_profile.phone
                zipcode = current_user_profile.zipcode
            elif shipping_form.is_valid():
                shipping_info = shipping_form.save()
                full_name = f"{shipping_info.shipping_first_name} {shipping_info.shipping_last_name}"
                email = shipping_info.shipping_email
                shipping_address = f"{shipping_info.shipping_address1}, {shipping_info.shipping_state}, {shipping_info.shipping_country}"
                phone = shipping_info.shipping_phone 
                zipcode = shipping_info.shipping_zipcode
            else:
                # Fallback directly into the final view context if validation fails
                context = {
                    "shipping_form": shipping_form,
                    "profile": current_user_profile,
                    "cart_items": cart_items_processed, 
                    "grand_totals": grand_total,
                    "shipping_cost": 20.00,
                }
                return render(request, 'payment/checkout.html', context)

            selected_payment = request.POST.get('payment_method')
            
            new_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                phone=phone,
                zipcode=zipcode,
                payment_method=selected_payment,
                amount_paid=grand_total,
                payment_status=False,
            )

            # SAVE ORDER ITEMS WITH THEIR COLORS AND SIZES
            for item in cart_items_processed:
                OrderItem.objects.create(
                    order=new_order,
                    product=item['product'],
                    quantity=item['qty'],
                    price=item['sale_price'] if item['is_sales'] else item['price'],
                    # Ensure color and size fields are present in your OrderItem Model!
                    color=item['color'],
                    size=item['size']
                )
            
            # Empty out user session basket upon order processing
            cart.clear()
            return redirect('order-confirmation', order_id=new_order.order_id)
            
    # ==========================================
    # GUEST USER WORKFLOW
    # ==========================================
    else: 
        shipping_form = ShippingForm(request.POST or None)

        if request.method == 'POST' and shipping_form.is_valid():
            shipping_info = shipping_form.save()
            selected_payment = request.POST.get('payment_method')
            
            new_order = Order.objects.create(
                user=None,
                full_name=f"{shipping_info.shipping_first_name} {shipping_info.shipping_last_name}", 
                email=shipping_info.shipping_email,
                shipping_address=f"{shipping_info.shipping_address1}, {shipping_info.shipping_state}, {shipping_info.shipping_country}",
                phone=shipping_info.shipping_phone,
                zipcode=shipping_info.shipping_zipcode,
                payment_method=selected_payment,
                amount_paid=grand_total, 
                payment_status=False,
            )

            # SAVE GUEST ORDER ITEMS WITH THEIR COLORS AND SIZES
            for item in cart_items_processed:
                OrderItem.objects.create(
                    order=new_order,
                    product=item['product'],
                    quantity=item['qty'],
                    price=item['sale_price'] if item['is_sales'] else item['price'],
                    color=item['color'],
                    size=item['size']
                )
            
            cart.clear()
            return redirect('order-confirmation', order_id=new_order.order_id)

    # ==========================================
    # FINAL RENDER CONTEXT PIPELINE
    # ==========================================
    context = {
        "shipping_form": shipping_form,
        "profile": current_user_profile,
        "cart_items": cart_items_processed, # Matches our unified loops natively!
        "grand_totals": grand_total, 
        "shipping_cost": 20.00,
    }
    return render(request, "payment/checkout.html", context)

"""
def checkout(request):
    #  variables at the very top for guest users that dont have or do not want to register
    current_user_profile = None 
    shipping_form = None

    #Get the cart
    cart = Cart(request)
    cart_products = cart.get_products()
    quantities = cart.get_quantities()
    totals = cart.cart_total()
    # Shipping charge
    #shipping_cost = 10.00  
    
    # Calculating the grand total logic while the sub total lies in the model
    grand_total = 0
    for product in cart_products:
        qty = quantities.get(str(product.id), 0)
        if product.is_sales:
            grand_total += (product.sale_price * qty)
            
        else:
            grand_total = grand_total + (product.price * qty)
            #grand_total += (product.price * qty)
    #####################################################################
    ####################################################################
    #####################################################################
    # This is for registered user
    if request.user.is_authenticated:
        # Using .filter().first() prevents a crash if the profile doesn't exist
        current_user_profile = Profile.objects.filter(user=request.user).first()
        shipping_user = ShippingAddress.objects.filter(user=request.user).order_by('-id').first()
        # This handles both displaying the form (GET) and saving it (POST)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        
        if request.method == 'POST':
            # Check if the checkbox was ticked in the HTML
            # Ensuring the 'name' in the HTML matches 'same_as_billing'
            is_same_address = request.POST.get('input-checkbox-1') 

            # If checkbox is TICKED and Profile exists, use Profile data
            if is_same_address and current_user_profile:
                full_name = f"{request.user.first_name} {request.user.last_name}"
                email = request.user.email
                shipping_address = f"{current_user_profile.address1}, {current_user_profile.state}, {current_user_profile.country}"
                phone = current_user_profile.phone
                zipcode = current_user_profile.zipcode
                
            # If NOT ticked, use the Shipping Form
            elif shipping_form.is_valid():
                shipping_info = shipping_form.save()
                full_name = f"{shipping_info.shipping_first_name} {shipping_info.shipping_last_name}"
                email = shipping_info.shipping_email
                shipping_address = f"{shipping_info.shipping_address1}, {shipping_info.shipping_state}, {shipping_info.shipping_country}"
                phone = shipping_info.shipping_phone # Ensure these fields exist in ShippingForm
                zipcode = shipping_info.shipping_zipcode
            else:
                # Handle invalid form here if necessary
                return render(request, 'payment/checkout.html', {'shipping_form': shipping_form})

           
            selected_payment = request.POST.get('payment_method')
             # Create the Order using the variables determined above
            new_order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                phone=phone,
                zipcode=zipcode,
                payment_method=selected_payment,
                amount_paid=grand_total,
                payment_status=False,
            )

            for product in cart_products:
                product_id = str(product.id)
                qty = quantities.get(product_id)
                price = product.sale_price if product.is_sales else product.price
                subtotal = qty * price

                OrderItem.objects.create(
                    order=new_order,
                    product=product,
                    quantity=qty,
                    price=price
                )
            
            # Redirect using the new UUID
            return redirect('order-confirmation', order_id=new_order.order_id)
            
    else: # Guest Users
        #####################################################################
        ####################################################################
        #####################################################################
      
        # Guests never have an 'instance' because they aren't in the database
        shipping_form = ShippingForm(request.POST or None)

        if request.method == 'POST' and shipping_form.is_valid():
            # For guests, i save the shipping form but it won't have a user attached
            shipping_info = shipping_form.save()

            #Capture the radio button value in the html
            selected_payment = request.POST.get('payment_method')
            
            # Creating an Order and map the shipping_form fields to the Order model
            new_order = Order.objects.create(
                user=None,
                full_name=f"{shipping_info.shipping_first_name} {shipping_info.shipping_last_name}", # or whatever your field name is
                email=shipping_info.shipping_email,
                shipping_address=f"{shipping_info.shipping_address1}, {shipping_info.shipping_state}, {shipping_info.shipping_country}",
                phone = shipping_info.shipping_phone,
                zipcode = shipping_info.shipping_zipcode,
                payment_method=selected_payment,
                amount_paid=grand_total, # Using your calculated grand_total
                payment_status=False,
            )

            for product in cart_products:
                product_id = str(product.id)
                qty = quantities.get(product_id)
                price = product.sale_price if product.is_sales else product.price
                #subtotal = qty * price

                OrderItem.objects.create(
                    order=new_order,
                    product=product,
                    quantity=qty,
                    price=price
                )
            
            #Redirect using the new UUID
            return redirect('order-confirmation', order_id=new_order.order_id)


    # 3. Final Render (Notice this is outside the if/else to avoid repetition)
    context = {
        "shipping_form": shipping_form,
        "profile": current_user_profile,
        "cart_products": cart_products, 
        "quantities": quantities, 
        "grand_totals": grand_total, # This fills the span on refresh
        "shipping_cost": 20.00,
    }
    return render(request, "payment/checkout.html", context)
"""    




def order_confirmation(request, order_id):
    #  Initialize variables to None (Guests won't have these)
    current_user_profile = None
    shipping_user = None
    

    #  Core Order Data that works for both Guests and Members
    # This uses the UUID from the URL to find the specific receipt
    order = get_object_or_404(Order, order_id=order_id)
    items = OrderItem.objects.filter(order=order)

    # query User-Specific models if they are logged in
    if request.user.is_authenticated:
        current_user_profile = Profile.objects.filter(user=request.user).first()
        shipping_user = ShippingAddress.objects.filter(user=request.user).first()

    #  Clearing the session cart for EVERYONE after order has been saved.
    cart = Cart(request)
    cart.clear()
    print("Cart after clear:", request.session.get('session_key'))


         

    context = {
        "profile": current_user_profile,
        "shipping_form": shipping_user,
        'order': order,
        'ordered_items': items,
        'bank_info': settings.BANK_DETAILS 
    }

    #  RETURN outside the IF block so Guests see the page too!
    return render(request, "payment/order-confirmation.html", context)



def payment_success(request):
    # get the last order placed by this user
    try:
        order = Order.objects.filter(user=request.user).latest('date_ordered')
        ordered_items = OrderItem.objects.filter(order=order)
    except Order.DoesNotExist:
        return redirect('home')

    context = {
        'order': order,
        'ordered_items': ordered_items,
    }
    return render(request, 'payment/payment-success.html', context)




########################################################################################
############################## Admin Dashboard #######################################
########################################################################################
### Admin Dashboard
@user_passes_test(is_superuser, login_url='/')
def admin_dashboard(request):
    if not request.user.is_staff :
        # Redirect non-staff users or show an error
        return redirect('home') 

    # Time frame for "recent" activity (7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)

    # --- Data Fetching ---
    
    # Recent Activity and Key Counts
    #recent_contacts = Contact.objects.filter(date_submitted__gte=seven_days_ago).order_by('-date_submitted')#[:5]
    recent_contacts = Contact.objects.all().order_by('-date_submitted')
    contact_count = Contact.objects.count()
    
    # New Subscribers (Last 7 Days)
    new_subscribers_7_days = NewsletterSubscriber.objects.filter(date_subscribed__gte=seven_days_ago).order_by('-date_subscribed')
    #new_subscribers = NewsletterSubscriber.objects.all().order_by('-date_subscribed')
    subscribers_count = NewsletterSubscriber.objects.count()
    coaching_requests = BasketballCoachingRegistration.objects.all().order_by('-registration_date')
    coaching_request_count = BasketballCoachingRegistration.objects.count()
    fitness_requests = FitnessRegistration.objects.all().order_by('-created_at')
    fitness_count = FitnessRegistration.objects.count()
    
    kitchen_bookings = KitchenBooking.objects.all().order_by('-created_at')
    kitchen_booking_count = KitchenBooking.objects.count()


    recent_orders = Order.objects.all().order_by('-date_ordered')
    total_revenue = Order.objects.filter(payment_status=True).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_revenue_in_dollars = total_revenue / 1500
    
    
    pending_orders_count = Order.objects.filter(payment_status=False).count()
    products = Product.objects.filter().order_by('-pieces')

    if request.method == 'POST':

        # PAYMENT STATUS UPDATE
        if 'payment-status' in request.POST:
            payment_status = request.POST.get('payment-status')
            payment_uuid = request.POST.get('payment-uuid')
            
            verify_order = Order.objects.filter(order_id=payment_uuid)
            if payment_status == 'true':
                verify_order.update(payment_status=True)
            else:
                verify_order.update(payment_status=False)
                
            messages.success(request, "Payment Status Updated")
            return redirect('admin-dashboard')

        #  SHIPPING Status
        if 'shipping-status' in request.POST:
            status = request.POST.get('shipping-status')
            order_uuid = request.POST.get('shipping_uuid')
            
            order_query = Order.objects.filter(order_id=order_uuid)
            now = datetime.datetime.now()
            
            if status == 'true':
                order_query.update(shipped=True, payment_status=True, date_shipped=now)
            else:
                order_query.update(shipped=False, payment_status=False) # Removed date_shipped update for unshipped
                
            messages.success(request, "Shipping Status Updated")
            return redirect('admin-dashboard')

        # Delivery Status
        if 'delivery-status' in request.POST:
            status = request.POST.get('delivery-status')
            order_uuid = request.POST.get('delivery_uuid')
            order_query = Order.objects.filter(order_id=order_uuid)
            current_time = datetime.datetime.now()
            
            if status == 'true':
                order_query.update( shipped=True,  payment_status=True,  date_shipped=current_time, date_delivered=current_time)
                messages.success(request, "Order Marked as Delivered successfully.")
            else:# Reverting back to basic pending states
                order_query.update(shipped=False, payment_status=False, date_delivered=None) # Clears out delivery timestamp safely
                messages.success(request, "Order delivery status reverted to pending.")

            return redirect('admin-dashboard')

    
    
    # ==========================================
    # FINAL RENDER CONTEXT PIPELINE
    # ==========================================
    orders_data = OrderItem.objects.all()
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)

    order_values = pd.DataFrame(
                orders_data.values('product__name', 'product__sports', 'quantity', 'price', 'color', 'size', 
                                    'order__date_ordered', 'order__amount_paid', 'order__payment_status'))
    
    # Always make sure that the (pandas datetime object) is converted to a string object before casting it to json
    order_values['order__date_ordered'] = (pd.to_datetime(order_values['order__date_ordered']))
    order_values = order_values.sort_values(by='order__date_ordered', ascending=False)
    order_values['order__date_ordered'] = order_values['order__date_ordered'].dt.date
    order_values['order__date_ordered'] = order_values['order__date_ordered'].astype("string")
   
    ########################################################################################
    ########################################################################################
    ########################################################################################
    # Daily Operational Revenue
    revenue_values = order_values.groupby(['order__date_ordered'])['order__amount_paid'].sum().reset_index()
    revenue_labels = revenue_values['order__date_ordered'].astype(str).tolist()
    revenue_data = revenue_values['order__amount_paid'].astype(float).tolist()

    # Market Share by Sport
    sport_distribution = order_values.groupby(['product__sports'])['quantity'].count().reset_index().sort_values(by='quantity', ascending=False)
    sport_labels = sport_distribution['product__sports'].tolist()
    sport_data = sport_distribution['quantity'].tolist()

    # Product Velocity Matrix
    product_category = order_values.groupby(['product__name'])['quantity'].count().reset_index().sort_values(by='quantity', ascending=False)
    product_labels = product_category['product__name'].tolist()
    product_data = product_category['quantity'].tolist()
   
    # --- Payment Status (Pending vs Paid) ---
    payment_df = order_values.groupby(['order__payment_status'])['order__amount_paid'].count().reset_index()
    #payment_status_labels = payment_df['order__payment_status'].tolist()
    #payment_status_series = payment_df['order__amount_paid'].astype(float).tolist()



    # 1. Get your raw groupby data exactly as you had it
    payment_df = order_values.groupby(['order__payment_status'])['order__amount_paid'].count().reset_index()

    # 2. Get the total sum of counts to calculate the percentage share
    total_orders = payment_df['order__amount_paid'].sum()

    # 3. Explicitly build the lists with 'Paid' first so it matches your green color index
    payment_status_labels = ['Paid', 'Pending']

    # 4. Manually extract the specific calculations for each status
    # This explicitly pairs the correct math with the labels above, regardless of DB order
    paid_count = payment_df[payment_df['order__payment_status'] == True]['order__amount_paid'].sum()
    pending_count = payment_df[payment_df['order__payment_status'] == False]['order__amount_paid'].sum()

    # Convert to percentages
    paid_pct = round((paid_count / total_orders) * 100, 1) if total_orders > 0 else 0
    pending_pct = round((pending_count / total_orders) * 100, 1) if total_orders > 0 else 0

    payment_status_series = [paid_pct, pending_pct]


   
    ########################################################################################
    ########################################################################################
    
    context = {
        'orders': Order.objects.all().count(),
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'total_revenue_in_dollars': total_revenue_in_dollars,
        'pending_orders_count': pending_orders_count,
        'total_shipped': Order.objects.filter(shipped=True).count(),
        'products': products,

        'recent_contacts': recent_contacts,
        'contact_count': contact_count,
        'new_subscribers': new_subscribers_7_days,
        'subscribers_count': subscribers_count,
        'coaching_requests': coaching_requests,
        'coaching_request_count': coaching_request_count,
        'fitness_requests': fitness_requests,
        'fitness_count': fitness_count,
        'kitchen_bookings': kitchen_bookings,
        'kitchen_booking_count': kitchen_booking_count,

        # PASS JSON DATA TO TEMPLATE
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),

        'sport_labels': json.dumps(sport_labels),
        'sport_data': json.dumps(sport_data),

        'product_labels': json.dumps(product_labels),
        'product_data': json.dumps(product_data),

        'payment_status_labels': json.dumps(payment_status_labels),
        'payment_status_series': json.dumps(payment_status_series),



    }

    return render(request, 'payment/admin-dashboard.html', context)                
###################################################################################
########################################################################################
######################################################################################
########################################################################################
### Admin Dashboard
@user_passes_test(is_superuser, login_url='/')
def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    items = OrderItem.objects.filter(order=order)

    
    
    context = {
        'order': order,
        'ordered_items': items,
    }

    return render(request, 'payment/order-details.html', context)  




