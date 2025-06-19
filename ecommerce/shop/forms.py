from django import forms
from django_countries import countries
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
import inspect
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class BillingDetailsForm(forms.Form):
    # Personal Information
    first_name = forms.CharField(
        label=_("First Name *"),
        label_suffix='',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'given-name'
        }),
        error_messages={
            'required': _('Please enter your first name'),
        }
    )
    
    last_name = forms.CharField(
        label=_("Last Name (optional)"), 
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'family-name'
        }),
        error_messages={
            'required': _('Please enter your last name'),
        }
    )

    # Address Information
    street_address = forms.CharField(
        label=_("Street Address (optional)"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('House number and street name'),
            'autocomplete': 'street-address'
        }),
        error_messages={
            'required': _('Please enter your street address'),
        }
    )
    
    apartment_suite = forms.CharField(
        label=_("Apartment, suite, unit etc. (optional)"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Apartment, suite, unit etc.'),
            'autocomplete': 'address-line2'
        })
    )
    
    town_city = forms.CharField(
        label=_("Town / City *"),
        label_suffix='',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'address-level2'
        }),
        error_messages={
            'required': _('Please enter your town/city'),
        }
    )
    
    state_country = forms.ChoiceField(
        label=_("Country *"),
        label_suffix='',
        required=True,
        choices=countries,
        widget=CountrySelectWidget(attrs={
            'class': 'form-control country-select',
            'data-priority-countries': ['KE', 'TZ', 'UG', 'US', 'GB', 'DE']
        }),
        initial='KE',
        error_messages={
            'required': _('Please select your country'),
        }
    )
    
    postcode = forms.CharField(
        label=_("Postcode / ZIP *"),
        label_suffix='',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'postal-code'
        }),
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9\- ]+$',
            message=_('Enter a valid postal code')
        )],
        error_messages={
            'required': _('Please enter your postal code'),
        }
    )
    
    # Contact Information
    email = forms.EmailField(
        label=_("Email Address *"),
        label_suffix='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'placeholder': 'example@gmail.com'
        }),
        error_messages={
            'required': _('Please enter your email address'),
            'invalid': _('Enter a valid email address'),
        }
    )
    
    phone = forms.CharField(
        label=_("Phone Number"),
        required=False,
        widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'type': 'tel',
                    'placeholder': '254712345678',
                }),
        error_messages={
            'required': _('Please enter your phone number'),
            'invalid': _('Enter a valid phone number'),
        }
    )    
    # Account Options
    create_account = forms.BooleanField(
        label=_("Create an account?"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-bs-toggle': 'collapse',
            'data-bs-target': '#accountFields'
        })
    )
    
    # password = forms.CharField(
    #     label=_("Create Password"),
    #     required=False,
    #     widget=forms.PasswordInput(attrs={
    #         'class': 'form-control',
    #         'autocomplete': 'new-password'
    #     }),
    #     help_text=_("Required if creating an account"),
    #     validators=[RegexValidator(
    #         regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
    #         message=_('Password must be at least 8 characters with letters and numbers')
    #     )]
    # )
    
    ship_to_different_address = forms.BooleanField(
        label=_("Ship to a different address?"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-bs-toggle': 'collapse',
            'data-bs-target': '#shippingAddress'
        })
    )

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
    
    accept_terms = forms.BooleanField(
        label=_("I have read and accept the terms and conditions"),
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        error_messages={
            'required': _('You must accept the terms and conditions'),
        }
    )

    # # Order notes
    # order_notes = forms.CharField(
    #     label=_("Order Notes (optional)"),
    #     required=False,
    #     widget=forms.Textarea(attrs={
    #         'class': 'form-control',
    #         'rows': 4,
    #         'placeholder': _('Notes about your order, e.g. special delivery instructions')
    #     })
    # )
