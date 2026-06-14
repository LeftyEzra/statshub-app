
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class BasketballCoachingRegistration(models.Model):
    # Registration Type Selection
    REGISTRATION_TYPE_CHOICES = [('parent', 'Individual Parent / Guardian'),('school', 'School / Institution')]
   
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    registration_type = models.CharField(max_length=10, choices=REGISTRATION_TYPE_CHOICES, default='parent')
    school_name = models.CharField(max_length=200, blank=True, null=True)
    age_or_grade_level = models.CharField(max_length=100, )
    num_of_players = models.PositiveIntegerField(default=1, verbose_name="Number of Players / Kids")
    additional_info = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.registration_type == 'school' and self.school_name:
            return f"School: {self.school_name} - {self.age_or_grade_level}"
        return f"Parent: {self.full_name} - {self.age_or_grade_level}"

    class Meta:
        
        verbose_name_plural = "Basketball Registrations"



# 1. FITNESS & PERFORMANCE REGISTRATION
class FitnessRegistration(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss / Management'),
        ('muscle_gain', 'Strength & Muscle Hypertrophy'),
        ('athletic_perf', 'Elite Athletic Performance Tuning'),
        ('endurance', 'Cardiovascular Conditioning'),
    ]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    AGE_RANGE = [('15+', '15-19'), ('20+', '20-24'), ('25+', '25-29'),
                 ('30+', '30-34'), ('35+', '35-39'), ('40+', '40-44'),
                 ('45+', '45-49'), ('50+', '50+')]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Physiological Metrics
    age = models.CharField(max_length=20, choices=AGE_RANGE, default='15+')
    gender_type = models.CharField(max_length=20, choices=GENDER_CHOICES, default='M')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kilograms")
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in centimeters")
    
    # Health & Background Context
    fitness_goals = models.CharField(max_length=20, choices=GOAL_CHOICES)
    medical_conditions = models.TextField("Injuries or Medical Conditions", help_text="State any heart issues, bone/joint pain, high blood pressure, etc.", blank=True, null=True)
    current_activity_level = models.CharField(max_length=50, help_text="e.g., Sedentary, 1-2 times a week, Elite Athlete")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fitness: {self.full_name}"

    class Meta:
        verbose_name_plural = 'Fitness Requests'     


# 2. PERFORMANCE KITCHEN & CATERING SERVICE
class KitchenBooking(models.Model):
    EVENT_CHOICES = [
        ('party', 'Social Party / Celebration'),
        ('sports_event', 'Sports Tournament / Team Catering'),
        ('corporate', 'Corporate Event'),
        ('meal_prep', 'Bulk Athlete Meal Prep Contract'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Event Logistics
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    event_date = models.DateField(default=timezone.now)
    estimated_guests = models.PositiveIntegerField(default=0)
    
    # Dietary Prefs
    menu_requirements = models.TextField("Menu Preferences & Details", help_text="Describe preferred local/intercontinental dishes, buffet or plated setup.")
    allergies_restrictions = models.TextField("Allergies or Dietary Restrictions", blank=True, null=True, help_text="e.g., Peanut allergies, Vegan, Gluten-Free options required")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kitchen:  {self.full_name} - {self.event_date}"


    class Meta:
        verbose_name_plural = 'Kitchen Bookings'     


# 3. ELITE CAREGIVER SERVICE
class CaregiverRequest(models.Model):
    RELATION_CHOICES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('self', 'Myself'),
        ('other', 'Other Relative / Dependent'),
    ]

    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    
    client_name = models.CharField("Your Name (Primary Contact)", max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Recipient Details
    recipient_name = models.CharField("Recipient Full Name", max_length=100)
    gender_type = models.CharField(max_length=20, choices=GENDER_CHOICES, default='M')
    
    relationship = models.CharField("Relationship to Recipient", max_length=10, choices=RELATION_CHOICES)
    recipient_age = models.PositiveIntegerField(default=0)
    
    # Care Requirements
    primary_medical_condition = models.TextField("Primary Medical Condition / Needs", help_text="e.g., Stroke recovery, mobility assistance, post-surgery care, elderly monitoring")
    special_instructions = models.TextField("Special Instructions or Routines", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Caregiver Request for {self.recipient_name} by {self.client_name}"


    class Meta:
        verbose_name_plural = 'Caregiver Requests'     
