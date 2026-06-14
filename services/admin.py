from django.contrib import admin
#Import the User contrib.auth.models
from django.contrib.auth.models import User

from .models import KitchenBooking, FitnessRegistration, CaregiverRequest, BasketballCoachingRegistration




# Register your models here.
#admin.site.register(GalleryImages)
@admin.register(BasketballCoachingRegistration)
class BasketballCoachingRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'registration_type', 'school_name', 
                    'age_or_grade_level', 'num_of_players', 'registration_date', 'additional_info')

    search_fields = ('full_name',) 
    ordering = ('registration_date', 'full_name',)

#admin.site.register(GalleryImages)
@admin.register(FitnessRegistration)
class FitnessRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'phone', 'age',  'gender_type','weight_kg', 'height_cm',
                  'fitness_goals', 'medical_conditions','current_activity_level', 'created_at')
    search_fields = ('full_name',) 
    ordering = ('created_at', 'full_name',)


@admin.register(CaregiverRequest)
class CaregiverRequestAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'email', 'phone', 'recipient_name', 'gender_type', 'relationship', 'recipient_age',
                   'primary_medical_condition', 'special_instructions', 'created_at')
    search_fields = ('full_name',) 
    ordering = ('created_at', 'client_name',)


@admin.register(KitchenBooking)
class KitchenBookingAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'event_type', 'event_date',
                     'estimated_guests', 'menu_requirements', 'allergies_restrictions', 'created_at' )
    search_fields = ('full_name',) 
    ordering = ('created_at', 'full_name',)