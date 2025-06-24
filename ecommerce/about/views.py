from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from shop.models import CustomerTestimonials

# Create your views here.
class AboutView(TemplateView):
    template_name = 'about/about.html'
    extra_context = {
        'page': 'about',
        'page_name': 'About Us',
        'customer_testimonies': CustomerTestimonials.objects.all()
    }