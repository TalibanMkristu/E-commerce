from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# Create your views here.
class AboutView(TemplateView):
    template_name = 'about/about.html'
    extra_context = {
        'page': 'about',
        'page_name': 'About Us'
    }