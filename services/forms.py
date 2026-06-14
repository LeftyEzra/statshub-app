from django import forms
from .models import FitnessRegistration, KitchenBooking, CaregiverRequest, BasketballCoachingRegistration
from django.forms import inlineformset_factory




# Fitness Form
class BasketballCoachingForm(forms.ModelForm):
    class Meta:
        model = BasketballCoachingRegistration
        fields = ('full_name', 'email', 'phone', 'registration_type', 'school_name', 
                   'age_or_grade_level', 'num_of_players', 'additional_info', )



# Fitness Form
class FitnessForm(forms.ModelForm):
    class Meta:
        model = FitnessRegistration
        fields = ('user', 'full_name', 'email', 'phone', 'age', 'weight_kg', 'height_cm',
                  'fitness_goals', 'medical_conditions','current_activity_level')

       
#Care Giving Form
class CaregiverForm(forms.ModelForm):
    class Meta:
        model = CaregiverRequest
        fields = ('client_name', 'email', 'phone', 'recipient_name', 'relationship', 'recipient_age',
                   'primary_medical_condition', 'special_instructions')

# Kitchen Model
class KitchenBookingForm(forms.ModelForm):
    class Meta:
        model = KitchenBooking
        fields = [
            'full_name', 'email', 'phone', 'event_type', 
            'event_date', 'estimated_guests', 'menu_requirements', 'allergies_restrictions'
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input' }),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'type': 'tel'}),
            'event_type': forms.Select(attrs={'class': 'form-control-has-validation form-control-last-child'}),
            'event_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'estimated_guests': forms.NumberInput(attrs={'class': 'form-input'}),
            'menu_requirements': forms.Textarea(attrs={'class': 'form-input'}),
            'allergies_restrictions': forms.Textarea(attrs={'class': 'form-input'}),
        }
