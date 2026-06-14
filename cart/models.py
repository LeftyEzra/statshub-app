from django.db import models

# Create your models here.
"""
from django.contrib.auth.models import User
from store.models import Product

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE) # Ties item to a specific person
    product = models.ForeignKey(Product, on_delete=CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
"""