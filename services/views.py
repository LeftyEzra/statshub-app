from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FitnessRegistration, KitchenBooking, CaregiverRequest, BasketballCoachingRegistration
from .forms import KitchenBookingForm, FitnessForm, CaregiverForm, BasketballCoachingForm





# BASKETBALL COACHING VIEW
def basketball_coaching(request):

    if request.method == "POST":
        form = BasketballCoachingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Form Submited Successfully")
            return redirect('basketball-coaching')
        else:
            pass
    else: 
        form = BasketballCoachingForm()

    return render(request, 'coaching.html', {"form" : form,}) 



# FITNESS VIEW
def fitness_services(request):
    if request.method == 'POST':
        FitnessRegistration.objects.create(
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            age=request.POST.get('age'),
            weight_kg=request.POST.get('weight_kg'),
            height_cm=request.POST.get('height_cm'),
            fitness_goals=request.POST.get('fitness_goals'),
            medical_conditions=request.POST.get('medical_conditions'),
            current_activity_level=request.POST.get('activity_level')
        )
        messages.success(request, "Fitness Intake Profile created successfully! Our Lead Coach will contact you for your fitness assessment.")
        return redirect('fitness-services')
        
    return render(request, 'fitness.html')

# CATERING KITCHEN VIEW
def kitchen_services(request):

    if request.method == "POST":
        form = KitchenBookingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, "Catering request submitted! Our culinary coordinator will call you shortly to finalize the menu choices.")
            return render(request, 'kitchen.html', {
                    'form': KitchenBookingForm()
                })


        else:
            pass
    else: 
        form = KitchenBookingForm()

    return render(request, 'kitchen.html', {"form" : form,}) 


# CAREGIVER VIEW
def caregiver_services(request):
    if request.method == 'POST':
        CaregiverRequest.objects.create(
            client_name=request.POST.get('client_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            recipient_name=request.POST.get('recipient_name'),
            relationship=request.POST.get('relationship'),
            recipient_age=int(request.POST.get('recipient_age', 0)),
            primary_medical_condition=request.POST.get('medical_condition'),
            special_instructions=request.POST.get('instructions')
        )
        messages.success(request, "Caregiver inquiry recorded securely. Our healthcare officer will schedule an assessment call immediately.")
        return redirect('caregiver-services')
        
    return render(request, 'caregiver.html')
