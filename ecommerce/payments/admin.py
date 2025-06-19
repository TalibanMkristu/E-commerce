from django.contrib import admin
from .models import SavedPaymentMethod, Order

@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_brand', 'last4_display', 'expiry_display', 'is_expired')
    list_filter = ('card_brand', )
    search_fields = ('user__username', 'card_last4')
    
    def last4_display(self, obj):
        return f"**** **** **** {obj.card_last4}"
    last4_display.short_description = 'Card Number'
    
    def expiry_display(self, obj):
        return obj.formatted_expiry
    expiry_display.short_description = 'Expiry'
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True

admin.site.register(Order)