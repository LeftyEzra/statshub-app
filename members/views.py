from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .forms import SignupUserForm, UpdateUserForm, UpdatePasswordForm, UserInfoForm
from django.contrib.auth import update_session_auth_hash
from store.models import Profile
import json
from cart.cart import Cart

# Create your views here.




#Login view
def login_user(request):
    # Django authentication code
    if request.method == 'POST': # If the users goes to the login page and fill out the form
        username = request.POST["username"] # Username
        password = request.POST["password"] # Password
        user = authenticate(request, username=username, password=password) # Check if the username and password variable are correct
        if user is not None: # if the user fill the form and the variables are correct
            login(request, user)# log the user in
            #Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            #Get user saved cart from the database
            saved_cart = current_user.old_cart
            #Convert the old_cart field to python dictionary
            if saved_cart:
                # Convert the JSON string stored in the user's Profile.old_cart field
                # back into a Python dictionary so we can work with it.
                converted_cart = json.loads(saved_cart)

                # Initialize a new Cart object tied to the current session.
                cart = Cart(request)

                # Loop through each item in the saved cart dictionary.
                # 'key' is the variant key (e.g. "6-blue-43"),
                # 'value' is the dict containing id, qty, color, size.
                for key, value in converted_cart.items():
                    # Re-add each item into the current session cart.
                    # We pull out the actual fields from the saved dict:
                    # - product ID
                    # - quantity
                    # - color (default to "Default" if missing)
                    # - size (default to "Standard" if missing)
                    cart.add_to_database(
                        product=value['id'],
                        quantity=value['qty'],
                        color=value.get('color', "Default"),
                        size=value.get('size', "Standard")
                    )



            return redirect("home")   # Redirect to home page after a successful log in.
        elif password != password:
            messages.success(request, ("Incorrect Password... "))

        else:
            # Else if the password or username is incorrect, return an 'invalid login' error message.
            messages.success(request, ("Oops! Error Logging In, Try Again... "))
            return redirect('login-user') # Remain in login page.


    else:
        return render(request, 'authentication/login.html', {})


# Logout View
def logout_user(request):
    logout(request)
    messages.success(request, ("Thanks for spending some quality time with the web site today. You are logged out..."))
    return redirect('login-user')



# Create User Form
def register_user(request):
    if request.method == 'POST':
        # FIX: Simplified to the standard way of initializing the form with POST data
        form = SignupUserForm(request.POST) 
        
        if form.is_valid():
            form.save()
            return redirect('login-user')

    else:
        # GET request: initialize an empty form
        form = SignupUserForm()

    # Pass the form (with or without errors) back to the template
    return render(request, 'authentication/register_user.html', {"form": form})



# Updte user info/profile
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            # Automatic log in behind the scenes
            login(request, current_user)
            messages.success(request, "Your Profile Has Been Updated...")
            return redirect('home')
        return render(request, 'authentication/update-user.html', {'user_form':user_form})

    else:
        messages.success(request, "Your Must Be Logged In To Access That Page...")
        return redirect('home')     


#Update Password Method 2
def update_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = UpdatePasswordForm(request.user, request.POST)# The form takes the user object
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                # Automatic log in
                #login(request, current_user)
                messages.success(request, "Your Password Has Been Updated, Please Log In Again")
                return redirect('login-user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update-password')
        else:
            form = UpdatePasswordForm(request.user)
            return render(request, 'authentication/update-password.html', {'form': form,})

    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')



#Update user info
def update_info(request):
    if request.user.is_authenticated: # If user is logged in
        #current user address
        current_user = Profile.objects.get(user__id=request.user.id)

        #Get current User shipping address
        #shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #Get user info form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #Get user shipping form
        #shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid():# or shipping_form.is_valid():
            form.save()
            #shipping_form.save()

            messages.success(request, "Your Info Has Been Updated...")
            return redirect('home')
        return render(request, 'authentication/update-user-info.html', {'form':form, })

    else:
        messages.success(request, "Your Must Be Logged In To Access That Page...")
        return redirect('home')