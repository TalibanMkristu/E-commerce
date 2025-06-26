from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Contacts
from django.urls import reverse
from django.contrib import messages
from django.utils.html import strip_tags
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomerMessages


# Create your views here.
class ContactView(TemplateView):
    template_name = 'contacts/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'contacts-us'
        context['page_name'] = 'Contact Us'
        contacts = Contacts.objects.filter( confirmed=True )
        context['contacts'] = contacts
        return context
    def post(self, request):
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()  # Remove whitespace
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = strip_tags(request.POST.get('message', ''))  # Remove HTML/JS

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return messages.error(self.request, "Invalid email address!")

            # Save to DB
            CustomerMessages.objects.update_or_create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            return redirect(reverse('contacts:contacts'))