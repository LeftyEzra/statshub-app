from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.db.models.signals import  post_save, pre_save
from django.dispatch import receiver
import datetime
import uuid
# Create your models here.

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_first_name = models.CharField(max_length=200, default='')
    shipping_last_name = models.CharField(max_length=200, default='')
    shipping_address1 = models.CharField(max_length=200)
    shipping_address2 = models.CharField(max_length=200,null=True, blank=True)
    shipping_city = models.CharField(max_length=200)
    shipping_state = models.CharField(max_length=200, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=200,null=True, blank=True)
    shipping_country = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=200, default='')
    shipping_email = models.EmailField("Email Address", default='')

    
    # Dont Pluralize address
    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address -{str(self.id)}'





# Create a user shipping address by default when user signs up
def create_shipping_address(sender, instance, created, **kwargs):
    if created:
        user_shipping_address = ShippingAddress(user=instance)
        user_shipping_address.save()

post_save.connect(create_shipping_address, sender=User)







PAYMENT_OPTIONS = [
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]
   
#Create order Model
class Order(models.Model):
    #Foriegn key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # This replaces the standard ID with a long, unique string
    order_id = models.UUIDField(default=uuid.uuid4, editable=False,  null=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=20, default='', blank=True, null=True)
    zipcode = models.CharField(max_length=20, default='', blank=True, null=True)
    shipping_address = models.TextField(max_length=20000)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_OPTIONS, default='Direct Bank Transfer')
    amount_paid =  models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    delivered = models.BooleanField(default=False)
    date_delivered = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
    def __str__(self):
        return f'Order - {str(self.id)}'
        
    # For the admin dashbord total items bought
    @property
    def total_quantity(self):
        # Set total items to zero
        total = 0
        all_items = self.items.all()# Get every item that belongs to this order        
        for item in all_items: # For every item found, adding it's quantity to the total
            total = total + item.quantity 

        return total     



# Auto Add Shipping Date
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now 
           
        if instance.delivered and not obj.delivered:
            instance.date_delivered = now    



#Create OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)


    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    # --- ADD THESE TWO FIELDS ---
    color = models.CharField(max_length=100, default="Default")
    size = models.CharField(max_length=100, default="Standard")

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Order Item - {str(self.id)}"

 