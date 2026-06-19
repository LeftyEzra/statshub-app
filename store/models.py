from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import  post_save # This automtically create a profile for every user that sign up
from django.utils.text import slugify
from django.utils import timezone
from team.models import Player

# Create your models here.



# =====================================================================
# THE BLUEPRINT
# =====================================================================
"""
models.Model: This is Django’s built-in powerhouse parent class. 
It is what connects Python code to the actual database. 
It contains all the default internal "magic" that allows one to run queries like 
.objects.all(), .save(), and .delete().

AutoSlugModel: This is a custom class. 
It is not built into Django. However, because its a written class AutoSlugModel(models.Model):, 
It inherits 100% of Django's default database powers, 
"""
class AutoSlugModel(models.Model):
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Looks for 'name' or 'title' automatically from whichever model uses it
            title_field = getattr(self, 'name', getattr(self, 'title', None))
            if title_field:
                self.slug = slugify(title_field)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True # Tells Django not to build a physical table named AutoSlugModel





# Creating models to keep track of category products
# Creating models to keep track of  products
# Creating models to keep track of customers
# Creating models to keep track of orders
# Create a extention of Customers Profile
# After pushing your model(s) to the data base go to the admin sessions to register the models
# Also create a new user model and associate it with the django authentication model


PRODUCT_CATEGORY = (
    ('Select Product', 'Select Product'),
    ('Ball', 'Ball'),
    ('Bags & Caps', 'Bags & Caps'),
    ('Socks', 'Socks'),
    ('Compressors', 'Compressors'),
    ('Footwears', 'Footwears'),
    ('Gloves', 'Gloves'),
    ('Sport Shoes', 'Sport Shoes'),
    ('Hoodies', 'Hoodies'),
    ('Shirts', 'Shirts'),
    ('Casual Shoes', 'Casual Shoes'),
    ('Watches', 'Watches'),
    ('Laptops', 'Laptops'),
    ('P.Lang', 'Programming Languages'),

)



SPORT_CATEGORY = (
    ('Select Sport', 'Select Sport'),('Basketball🏀', 'Basketball🏀'),('Boxing🥊', 'Boxing🥊',),
    ('Badmington🏸', 'Badmington🏸'),('Gym⛹', 'Gym⛹'),('Soccer⚽ ', 'Soccer⚽ '),('Football🏈⚽', 'Football🏈⚽'),
    ('Tracks & Fields🏃', 'Tracks & Fields🏃'), ('Rugby🏉', 'Rugby🏉'),('Volleyball🏐', 'Volleyball🏐'),
    ('Ping Pong🎾', 'Ping Pong🎾'),('Cricket', 'Cricket'),('Lawn Tennis🎾', 'Lawn Tennis🎾'),
)






class Colors(AutoSlugModel):
    name = models.CharField(max_length=30, unique=True)
    hex_code = models.CharField(max_length=7,  help_text="Example: #FFFFFF for white, #000000 for black")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Colors'     

class Sizes(models.Model):
    sizes = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.sizes    

    class Meta:
        verbose_name_plural = 'Sizes'         

CURRENT_CONDITION = (    
    ('New', 'Brand New'),
    ('Hot', 'Trending'),
    ('Acube', 'Pristine'), # Keeps 'Acube' in DB, but shows premium text to users Grade A Used (Pristine Condition)'
)

GENDER_CHOICES =  (
    ('Unisex', 'Unisex'),    
    ('Male', 'Male'),
    ('Female', 'Female'),
  
)

#Products model
class Product(AutoSlugModel):
    
    name = models.CharField("Name",max_length=50, unique=True)
    price        = models.DecimalField(default=0, decimal_places=2, max_digits=7)
    category     = models.CharField(max_length=15, choices=PRODUCT_CATEGORY, default='Select Product', blank=True,null=True)
    sports       = models.CharField(max_length=30, choices=SPORT_CATEGORY, default='Select Sports', blank=True,null=True)
    sizes        = models.ManyToManyField('Sizes', blank=True)
    colors       = models.ManyToManyField('Colors', blank=True)
    gender_type  = models.CharField(max_length=6, choices=GENDER_CHOICES, default='Unisex', blank=True,null=True )
    brand_type   = models.CharField(max_length=7, choices=CURRENT_CONDITION, default='', blank=True,null=True )
    description  = models.TextField(max_length=10000, default='',blank=True,null=True)
    image        = models.ImageField(upload_to='uploads/product/',blank=True,null=True)
    # Add Sales Stuff
    is_sales   = models.BooleanField(default=False)
    sales_price = models.DecimalField(default=0, decimal_places=2, max_digits=6, blank=True,null=True)
    pieces = models.PositiveIntegerField(default=1, blank=True, null=True)
    featured_player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='merchandise')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Products'    


# Action Photos Model
class GalleryImages(AutoSlugModel):
    name = models.CharField(max_length=20, default='', blank=True, null=True)
    images = models.ImageField(upload_to='uploads/Product_Gallery/',blank=True, null=True)  # This will automatically create a folder in the project directory.
    product = models.ForeignKey(Product, related_name='product_pictures', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        if self.product:
            return f"Image for {self.product.name}"
        return f"Gallery Image {self.id}"

    class Meta:
        verbose_name_plural = 'Product Image Gallery'



 
# Customers Review
class CustomerReview(AutoSlugModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    review_message = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)  # 1–5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"{self.customer_name} ({self.rating} stars)"



GENDER_CHOICES =  (
     
    ('Male', 'Male'),
    ('Female', 'Female'),
  
)
#Create Customer Profile
#Customer's model
class Profile(models.Model):
    #Associating this model with the django User authentication model
    user = models.OneToOneField(User, on_delete=models.CASCADE) # This is to associate 1 user to 1 profile
    gender  = models.CharField(max_length=6, choices=GENDER_CHOICES, default='Male', blank=True,null=True )
    date_modified = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=25, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    # The shopping cart is a python dict and its kinda complicated to save a python dict to the database
    # Convert the python dict shopping cart into string- save it in the database as a string and pull it out as a string
    # then convert it back as a dictionary.
    old_cart = models.CharField(max_length=200, blank=True,null=True) # This is for the users cart so when they logout and login they would see the product intheir cart
    same_as_billing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

#The create a user profile by default when user signs up from the signup form
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
# Automate the profile just created
post_save.connect(create_profile, sender=User)

