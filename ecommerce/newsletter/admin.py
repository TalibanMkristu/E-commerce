from django.contrib import admin
from .models import Subscriber, Newsletter

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed', 'is_confirmed')
    list_filter = ('is_confirmed',)
    search_fields = ('email',)
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        # Similar to the export view but for admin
        pass

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at')
    search_fields = ('subject', 'message')