from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Order, OrderItem, BillingAddress, Wishlist
from blog.models import Category
from django.urls import reverse, reverse_lazy
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
        items = Item.objects.all().order_by('-percentage_discount')
        categories = Category.objects.all()
        context['items'] = items
        context['categories'] = categories
            
        return context

class CartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            order.update_totals()
            context = {
                'page': 'Your Cart',
                'order': order,
                'order_items': order.items.all()
            }
            return render(self.request, 'shop/cart.html', context)
        except Order.DoesNotExist:
            messages.info(self.request, "You don't have an active order")
            return redirect("shop:shop")

class CheckOutView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('users:login')
    form_class = BillingDetailsForm
    template_name = 'shop/checkout.html'
    extra_context = {
        'page': 'checkout',
        'page_name': 'My CheckOut',
    }

    def dispatch(self, request, *args, **kwargs):
        # First, check for active order without triggering form processing
        if request.method == 'GET':
            if not Order.objects.filter(user=request.user, ordered=False).exists():
                messages.warning(request, "You don't have any active order to checkout. Make an order.")
                return redirect('shop:shop')
        
        # Only process form data if it's a POST request
        if request.method == 'POST':
            # Handle potential phone number format issues
            if 'phone_0' in request.POST:
                mutable_post = request.POST.copy()
                mutable_post['phone'] = mutable_post['phone_0']
                request.POST = mutable_post
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context['order'] = order
        except Order.DoesNotExist:
            messages.error(self.request, "No active order found.")
        return context
    
    def form_valid(self, form):
        user = self.request.user
        print(self.request.POST)
        print(form.cleaned_data)
        try:
            order = Order.objects.get(user=user, ordered=False)
            
            if hasattr(order, 'billing_address'):
                messages.info(self.request, "Billing address already exists for this order")
                return redirect('payments:checkout')
            
            # Process phone number safely
            phone = form.cleaned_data.get('phone')
            # if isinstance(phone, list):
            #     phone = phone[0] if phone else None
            
            BillingAddress.objects.create(
                user=user,
                order=order,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                street_address=form.cleaned_data.get('street_address'),
                apartment_suite=form.cleaned_data.get('apartment_suite'),
                town_city=form.cleaned_data.get('town_city'),
                state_country=form.cleaned_data.get('state_country'),
                email=form.cleaned_data.get('email'),
                phone=phone,
                postcode=form.cleaned_data.get('postcode'),
                
            ) 
            messages.success(self.request, 'Billing details saved successfully!')
            return redirect('payments:payments')

            
            
        except Order.DoesNotExist:
            messages.error(self.request, 'No active order found')
            return redirect('shop:cart')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors in the form.')
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('payments:payments')
    
    
class WishListView(TemplateView):
    template_name = 'shop/wishlist.html'
    extra_context = {
        'page': 'wishlist',
        'page_name': 'My WishList',
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist = Wishlist.objects.all()
        context['wishlist']=wishlist
        return context

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
            id = self.object.id , ordered = False
        )
        related_products = Item.objects.filter(
            category=self.object.category
        ).order_by('-percentage_discount')
        context['item'] = item
        context['order_item'] = order_item
        context['related_products']=related_products
        return context

class AddToCartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
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
                messages.info(request, f"{order_item.item.title} quantity was updated.")
            else:
                order.items.add(order_item)
                messages.info(request, f"{order_item.item.title} was added to your cart.")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, 
                ordered_date=ordered_date
            )
            order.items.add(order_item)
            messages.info(request, f"{order_item.item.title} was added to your cart.")
        
        return redirect("shop:cart")

class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
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
                messages.info(request, f"{order_item.item.title} was removed from your cart.")
                return redirect("shop:cart")
            else:
                messages.info(request, f"{order_item.item.title} was not in your cart.")
                return redirect("shop:product-single", slug=slug)
        else:
            messages.info(request, "You don't have an active order.")
            return redirect("shop:product-single", slug=slug)
        
class RemoveSingleItemFromCartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('users:login')
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
                    messages.info(request, f"{order_item.item.title} quantity was decreased.")
                else:
                    order.items.remove(order_item)
                    order_item.delete()
                    messages.info(request, f"{order_item.item.title} was removed from cart.")
                return redirect("shop:cart")
            else:
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )                
                messages.info(request, f"{order_item.item.title} was not in your cart.")
                return redirect("shop:product-single", slug=slug)
        else:
            messages.info(request, "You don't have an active order.")
            return redirect("shop:product-single", slug=slug)
        
class AddToWishlist(View):
    def get(self, request, slug, *a, **k):
        item = get_object_or_404(Item, slug=slug)
        wish = Wishlist.objects.get_or_create(
            item=item,
            user=self.request.user,
            ordered=False
        )
        if wish.item.filter(item__slug=item.slug).exists():
            wish.quantity += 1
            wish.save()
            messages.info(self.request, f"{wish.item.name} quantity increased.")
        else:
            wish.item.add(item)
            messages.success(self.request, f"{wish.item.name} added to wishlist.")
        return redirect(reverse('shop:wish-list'))
    
class RemoveFromWishlist(View):
    def get(self, request, slug, *a, **k):
        item = get_object_or_404(Item, slug=slug)
        wish = Wishlist.objects.filter(
            user = self.request.user,
            item=item,
            ordered=False,
        )
        if wish:
            if wish.item.filter(item__slug=item.slug).exists():
                if wish.quantity > 1:
                    wish.quantity -= 1
                    wish.save()
                    messages.info(self.request, f"{wish.item.name} quaantity decreased.")
                else:
                    wish.item.remove(wish.iten)
                    wish.delete()
                    messages.info(self.request, f"{wish.item.name} removed from wishlist.")
        return redirect(reverse('shop:wishlist'))