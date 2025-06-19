from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from payments.models import SavedPaymentMethod
from django.template.loader import render_to_string
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Checks for expiring or expired cards and notifies users'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        next_month = today.replace(month=today.month+1) if today.month < 12 else today.replace(year=today.year+1, month=1)
        
        # Cards expiring within 30 days
        expiring_soon = SavedPaymentMethod.objects.filter(
            card_exp_year=next_month.year,
            card_exp_month=next_month.month
        )
        
        # Already expired cards
        expired = SavedPaymentMethod.objects.filter(
            models.Q(card_exp_year__lt=today.year) |
            models.Q(card_exp_year=today.year, card_exp_month__lt=today.month)
        )
        
        # Send notifications
        for card in expiring_soon:
            self.send_expiry_notice(card, soon=True)
            
        for card in expired:
            self.send_expiry_notice(card, soon=False)
    
    def send_expiry_notice(self, card, soon=True):
        subject = "Your card is %sexpiring" % ("about to " if soon else "")
        message = render_to_string('emails/card_expiry_notice.html', {
            'card': card,
            'soon': soon
        })
        
        send_mail(
            subject,
            message,
            'noreply@yourdomain.com',
            [card.user.email],
            html_message=message
        )