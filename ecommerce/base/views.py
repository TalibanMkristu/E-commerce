from django.shortcuts import render, redirect
from django.views.generic import TemplateView

# Create your views here.

class IndexView(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'welcome to traxy collections'
        return context
    
class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'welcome home traxy collections'
        return context