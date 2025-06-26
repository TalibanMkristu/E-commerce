from django.contrib import admin
from .models import Item, OrderItem, Order, BillingAddress, CustomerTestimonials

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'price_before_discount', 
                    'percentage_discount', 'category', 'label', 'size',
                    'stock', )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'ordered_date', 'ordered', )
    list_filter = ('items', )

admin.site.register(BillingAddress)
admin.site.register(CustomerTestimonials)
