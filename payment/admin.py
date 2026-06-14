from django.contrib import admin
from.models import ShippingAddress, Order, OrderItem
# Register your models here.




@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user','shipping_first_name', 'shipping_last_name', 'shipping_address1',
                    'shipping_address2', 'shipping_city', 'shipping_state', 'shipping_zipcode',
                    'shipping_country', 'shipping_phone', 'shipping_email')
    search_fields = ('user','shipping_first_name', 'shipping_last_name',) 
    ordering = ('user','shipping_first_name', 'shipping_last_name',)


#admin.site.register(Order)
#admin.site.register(OrderItem)

#Merge profile info with user info
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display =('user','order_id', 'full_name', 'email', 'shipping_address',
                    'phone', 'zipcode', 'amount_paid', 'payment_method', 'payment_status',
                    'date_ordered', 'shipped', 'date_shipped', 'delivered','date_delivered')
    search_fields = ('user','full_name','order_id')
    readonly_fields = ("date_ordered",)
    ordering = ('user','full_name',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display =( 'order', 'product', 'quantity', 'price', )
    search_fields = ('order', 'product',) 
    ordering = ('order', 'product',)    

#admin.site.unregister(Order)   
#admin.site.register(Order, OrderAdmin)  