from django import forms
from .models import Wishlist

class CreateWishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Birthday Wishlist'
            })
        }

class ShareWishlistForm(forms.Form):
    email = forms.EmailField(required=False)
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Optional message'
        })
    )