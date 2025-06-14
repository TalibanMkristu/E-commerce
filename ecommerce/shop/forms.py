from django import forms
from django_countries import countries
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

class BillingDetailsForm(forms.Form):
    # Personal Information
    first_name = forms.CharField(
        label="First Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        label="Last Name", 
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Address Information
    street_address = forms.CharField(
        label="Street Address",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'House number and street name'
        })
    )
    
    apartment_suite = forms.CharField(
        label="Apartment, suite, unit etc. (optional)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Appartment, suite, unit etc: (optional)'
            })
    )
    
    town_city = forms.CharField(
        label="Town / City",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    state_country = forms.ChoiceField(
        label="State / Country",
        choices=countries,  # Add more countries as needed
        widget=CountrySelectWidget(attrs={'class': 'form-control'}),
        initial='KE',
    )
    
    postcode = forms.CharField(
        label="Postcode / ZIP *",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Contact Information
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    phone = PhoneNumberField(
        label="Phone",
        initial='+254',  # Kenya's country code
        required=True,
        widget=PhoneNumberPrefixWidget(
            attrs={
                'class': 'form-control',
            },
            widgets={
                # forms.Select(attrs={'class': 'form-control country-select'}),
                forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder':'254 712 345 678'
                    })                
            },
    ),
    )
    
    # Account Options
    create_account = forms.BooleanField(
        label="Create an Account?",
        required=False,
        widget=forms.CheckboxInput(attrs={

            })
    )
    
    
    ship_to_different_address = forms.BooleanField(
        label="Ship to different address",
        required=False,
        label_suffix= '',
        widget=forms.CheckboxInput(attrs={

        })
    )

    # Payment Method (New Fields)
    PAYMENT_CHOICES = [
        ('bank', 'Direct Bank Transfer'),
        ('check', 'Check Payment'),
        ('paypal', 'PayPal'),
    ]
    
    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    accept_terms = forms.BooleanField(
        label="I have read and accept the terms and conditions",
        label_suffix= '',
        required=True,
        # checked=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set priority countries (appear first in list)
        self.fields['state_country'].widget.attrs['data-priority-countries'] = ['KE', 'TZ', 'UG', 'US', 'GB', 'DE']    

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Set initial phone number value after form initialization
    #     if not self.is_bound and 'phone' not in self.initial:
    #         self.initial['phone']='=254'

    # def get_country_choices():
    #     """Generate sorted country code choices with country names"""
    #     choices = []
    #     for code, regions in sorted(COUNTRY_CODE_TO_REGION_CODE.items()):
    #         for region in regions:
    #             try:
    #                 country = pycountry.countries.get(alpha_2=region)
    #                 name = country.name
    #             except:
    #                 name = region
    #             choices.append((code, f"+{code} {name}"))
    #     return choices            