from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Order, OrderItem
from blog.models import Category
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .forms import BillingDetailsForm

# Create your views here.
class ShopView(ListView):
    model = Item
    template_name = 'shop/shop.html'
    paginate_by = 30
    extra_context = {
        'page': 'shop',
        'page_name': 'Products'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.all()
        categories = Category.objects.all()
        context['items'] = items
        context['categories'] = categories
            
        return context

class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'page': 'Your Cart',
                'order': order,
                'order_items': order.items.all()
            }
            return render(self.request, 'shop/cart.html', context)
        except Order.DoesNotExist:
            messages.info(self.request, "You don't have an active order")
            return redirect("shop:shop")

class CheckOutView(FormView):
    form_class = BillingDetailsForm
    template_name = 'shop/checkout.html'
    extra_context = {
        'page': 'checkout',
        'page_name': 'My CheckOut',
        
    }
    # success_url=
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.get(user=self.request.user, ordered=False)
        context['order']=order
        return context

class WishListView(TemplateView):
    template_name = 'shop/wishlist.html'
    extra_context = {
        'page': 'cart',
        'page_name': 'My WishList',
    }

class SingleProductView(DetailView):
    model = Item
    template_name = 'shop/single_product.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    extra_context = {
        'page': 'product-specific',
        'page_name': 'Product Specific',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = Item.objects.filter(
            id = self.object.id
        )
        order_item = OrderItem.objects.filter(
            id = self.object.id 
        )
        context['item'] = item
        context['order_item'] = order_item
        return context

class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Item quantity was updated.")
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, 
                ordered_date=ordered_date
            )
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
        
        return redirect("shop:cart")

class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item was removed from your cart.")
                return redirect("shop:cart")
            else:
                messages.info(request, "This item was not in your cart.")
                return redirect("shop:product-single", slug=slug)
        else:
            messages.info(request, "You don't have an active order.")
            return redirect("shop:product-single", slug=slug)
        
class RemoveSingleItemFromCartView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                    order_item.delete()
                messages.info(request, "This item quantity was updated.")
                return redirect("shop:cart")
            else:
                messages.info(request, "This item was not in your cart.")
                return redirect("shop:product-single", slug=slug)
        else:
            messages.info(request, "You don't have an active order.")
            return redirect("shop:product-single", slug=slug)        