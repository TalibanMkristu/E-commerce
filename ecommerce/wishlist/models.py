from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from shop.models import Item as Product
import uuid

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    name = models.CharField(max_length=100, default='My Wishlist')
    is_default = models.BooleanField(default=False)
    share_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_absolute_url(self):
        return reverse('wishlist:shared_wishlist', kwargs={'token': self.share_token})

    def get_items_count(self):
        return self.items.count()

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default wishlist per user
            Wishlist.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    desired_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Get notified when price drops to this amount"
    )

    class Meta:
        unique_together = ('wishlist', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.original_price = self.product.price
        super().save(*args, **kwargs)

@receiver(post_save, sender=Product)
def check_price_drop(sender, instance, **kwargs):
    if 'price' in kwargs.get('update_fields', []) or not kwargs.get('created', False):
        for item in WishlistItem.objects.filter(product=instance):
            if instance.price < item.original_price:
                if item.desired_price and instance.price <= item.desired_price:
                    # Send price drop notification
                    from django.core.mail import send_mail
                    send_mail(
                        f"Price Alert: {item.product.name} reached your desired price!",
                        f"The price of {item.product.name} has dropped to ${instance.price}.\n\nView it here: {instance.get_absolute_url()}",
                        settings.DEFAULT_FROM_EMAIL,
                        [item.wishlist.user.email],
                        fail_silently=False,
                    )
                item.original_price = instance.price
                item.save()