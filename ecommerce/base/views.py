from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from blog.models import Category
from shop.models import Order, OrderItem, Item,  CustomerTestimonials, Wishlist

# Create your views here.

class IndexView(TemplateView):
    template_name = 'base/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'welcome home vegegroccer'
        return context
    
class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'welcome home vegegroccer'
        items = Item.objects.all().order_by('-percentage_discount')[:30]
        categories = Category.objects.all()
        customer_testimonies = CustomerTestimonials.objects.all()
        wishlist = Wishlist.objects.filter(
            ordered = False,
            user = self.request.user
        )
        context = {
            'items': items,
            'categories': categories,
            'customer_testimonies': customer_testimonies,
            'wishlist':wishlist,            
        }        
        return context