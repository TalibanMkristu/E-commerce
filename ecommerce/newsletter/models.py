from django.db import models
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.utils import timezone

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    def __str__(self):
        return self.email
    
    def send_confirmation_email(self):
        subject = "Confirm your newsletter subscription"
        confirmation_link = f"{settings.SITE_URL}/newsletter/confirm/{self.confirmation_token}/"
        message = f"Please click this link to confirm your subscription: {confirmation_link}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )

class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.subject
    
    def send_to_subscribers(self):
        subscribers = Subscriber.objects.filter(is_confirmed=True)
        for subscriber in subscribers:
            send_mail(
                self.subject,
                self.message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=False,
            )
        self.sent_at = timezone.now()
        self.save()