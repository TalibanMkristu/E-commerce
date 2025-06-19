from django.db import models
from django.conf import settings
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())  
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Order

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
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="user", on_delete=models.SET_NULL, null=True, blank=True)
    orders = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)    
    customer_email = models.EmailField()
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=200, blank=True, null=True)
    plan_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, blank=True, null=True)  # monthly, yearly, etc.
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_details = models.JSONField(default=dict)  # Stores card info, PayPal details, etc.
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    opt_in_marketing = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_email} - {self.total_amount}"

    def total(self):
        return self.order.get_total()

class SavedPaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For card payments
    card_brand = models.CharField(max_length=50, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_exp_month = models.PositiveSmallIntegerField(null=True, blank=True)
    card_exp_year = models.PositiveSmallIntegerField(null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=50, blank=True)
    
    # For PayPal
    paypal_email = models.EmailField(blank=True)
    paypal_payer_id = models.CharField(max_length=50, blank=True)

      # Proper expiry fields (should NOT be encrypted since they're not considered highly sensitive alone)
    card_exp_month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    card_exp_year = models.PositiveSmallIntegerField()
    
    # Encrypted fields (requires PCI compliance)
    card_number = EncryptedCharField(models.CharField(max_length=16, blank=True))  # Full number
    card_name = EncryptedCharField(models.CharField(max_length=100, blank=True))  # Cardholder name
    
    @property
    def formatted_expiry(self):
        return f"{self.card_exp_month:02d}/{self.card_exp_year}"
    
    @property
    def is_expired(self):
        from datetime import date
        today = date.today()
        return (self.card_exp_year < today.year) or \
               (self.card_exp_year == today.year and self.card_exp_month < today.month)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(card_exp_month__gte=1) & models.Q(card_exp_month__lte=12),
                name="valid_exp_month"
            ),
            models.CheckConstraint(
                check=models.Q(card_exp_year__gte=2000) & models.Q(card_exp_year__lte=2100),
                name="valid_exp_year"
            )
        ]

    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.card_brand} ending in {self.card_last4}"
        return f"PayPal: {self.paypal_email}"