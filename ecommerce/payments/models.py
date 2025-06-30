# payments/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField

from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Order as ShopOrder

class Order(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('requires_action', 'Requires Action'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="payment_orders", on_delete=models.SET_NULL, null=True, blank=True)
    shop_order = models.ForeignKey(ShopOrder, on_delete=models.SET_NULL, null=True, blank=True)    
    customer_email = models.EmailField()
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_details = models.JSONField(default=dict)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_client_secret = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    opt_in_marketing = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} - {self.customer_email} - ${self.total_amount}"

    @property
    def is_paid(self):
        return self.payment_status == 'completed'

    def update_from_stripe(self, payment_intent):
        """Update order details from Stripe PaymentIntent"""
        self.stripe_payment_intent_id = payment_intent.id
        self.payment_reference = payment_intent.id
        self.payment_details = {
            'amount_received': payment_intent.amount_received,
            'payment_method': payment_intent.payment_method.id if payment_intent.payment_method else None,
            'charges': payment_intent.charges.data if hasattr(payment_intent, 'charges') else None,
            'status': payment_intent.status
        }
        
        if payment_intent.status == 'succeeded':
            self.payment_status = 'completed'
        elif payment_intent.status in ['requires_payment_method', 'requires_confirmation']:
            self.payment_status = 'requires_action'
        elif payment_intent.status == 'canceled':
            self.payment_status = 'failed'
        
        self.save()

class SavedPaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Card fields
    card_brand = models.CharField(max_length=50, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_exp_month = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    card_exp_year = models.PositiveSmallIntegerField(null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=50, blank=True)
    
    # PayPal fields
    paypal_email = models.EmailField(blank=True)
    paypal_payer_id = models.CharField(max_length=50, blank=True)

    # Encrypted sensitive fields
    card_number = EncryptedCharField(max_length=16, blank=True)
    card_name = EncryptedCharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Saved Payment Method'
        verbose_name_plural = 'Saved Payment Methods'

    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.card_brand.title()} ending in {self.card_last4}"
        return f"PayPal: {self.paypal_email}"

    @property
    def formatted_expiry(self):
        if self.card_exp_month and self.card_exp_year:
            return f"{self.card_exp_month:02d}/{self.card_exp_year}"
        return ""

    @property
    def is_expired(self):
        if not self.card_exp_month or not self.card_exp_year:
            return False
            
        current_year = timezone.now().year
        current_month = timezone.now().month
        return (self.card_exp_year < current_year) or \
               (self.card_exp_year == current_year and self.card_exp_month < current_month)

    def update_from_stripe(self, payment_method):
        """Update payment method details from Stripe PaymentMethod"""
        if payment_method.type == 'card':
            self.card_brand = payment_method.card.brand
            self.card_last4 = payment_method.card.last4
            self.card_exp_month = payment_method.card.exp_month
            self.card_exp_year = payment_method.card.exp_year
            self.stripe_payment_method_id = payment_method.id
            self.save()