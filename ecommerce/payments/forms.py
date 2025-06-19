from django import forms
import inspect
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class PaymentConfirmationsForm(forms.Form):
    # Payment Method
    PAYMENT_CHOICES = [
        ('bank', _('Credit / Debit card')),
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
        ('mpesa', _('M-Pesa')),
    ]
    
    payment_method = forms.ChoiceField(
        label=_("Payment Method"),
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False,
        error_messages={
            'required': _('Please select a payment method'),
        }
    )