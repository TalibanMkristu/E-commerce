from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Contacts

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