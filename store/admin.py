from django.contrib import admin
#Import the User contrib.auth.models
from django.contrib.auth.models import User
from .models import GalleryImages
from .models import Product
from .models import Colors, Sizes


from .models import CustomerReview
from .models import Profile



# Registration of Category
admin.site.register(GalleryImages)
admin.site.register(Colors)
admin.site.register(Sizes)
#admin.site.register(Order)

#Register Product in the Admin area
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'sports', 'gender_type',
                    'brand_type', 'description', 'image', 'is_sales', 'sale_price', 'pieces', 'featured_player',)
    search_fields = ('name', 'price', 'category', 'brand_type', 'is_sales', 'sale_price', 'gender_type', 'featured_player')    
    ordering = ('name', )
    earch_help_text = ('name',)
    filter_horizontal = ('colors', 'sizes',)
   
    def get_colors(self, obj):
            if obj.colors:
                return ", ".join([product.name for product in obj.colors.all()])
            return "No color"
    get_colors.short_description = 'Color'

    def get_sizes(self, obj):
            if obj.sizes:
                return ", ".join([product.size for product in obj.sizess.all()])
            return "No size"
    get_sizes.short_description = 'Size'



  

@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_image', 'product','review_message', 'rating', 'created_at')
    search_fields = ('customer_name','product',) 
    ordering = ('created_at', 'customer_name',)



##################################################################################
##################################################################################
##################################################################################
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'date_modified', 'phone', 'address1','address2', 'city', 'state', 'zipcode', 'country','same_as_billing')
    search_fields = ('user',) 
    ordering = ('date_modified', 'user',)
#Merge profile info with user info
class ProfileInline(admin.StackedInline):
    model = Profile

class UserAdmin(admin.ModelAdmin):
    model = User
    field = ['username', 'first_name', 'last_name','email']
    inlines = [ProfileInline]

#Unregistering the old user because of the newly added profile model
admin.site.unregister(User)

#Re-register the new way
admin.site.register(User, UserAdmin)
##################################################################################
##################################################################################
##################################################################################