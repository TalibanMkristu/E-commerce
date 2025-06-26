from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wishlist, WishlistItem
from shop.models import Item as Product
from shop.views import AddToCartView as add_to_cart
from .forms import CreateWishlistForm, ShareWishlistForm
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@login_required
def wishlist_dashboard(request):
    wishlists = request.user.wishlists.all()
    default_wishlist = request.user.wishlists.filter(is_default=True).first()
    return render(request, 'wishlist/dashboard.html', {
        'wishlists': wishlists,
        'default_wishlist': default_wishlist,
        'create_form': CreateWishlistForm(),
        'share_form': ShareWishlistForm()
    })

@login_required
def wishlist_detail(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    return render(request, 'wishlist/detail.html', {'wishlist': wishlist})

def shared_wishlist(request, token):
    wishlist = get_object_or_404(Wishlist, share_token=token)
    return render(request, 'wishlist/shared.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_id = request.POST.get('wishlist_id')
    
    if wishlist_id:
        wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    else:
        wishlist = request.user.wishlists.filter(is_default=True).first()
        if not wishlist:
            wishlist = Wishlist.objects.create(user=request.user, name='My Wishlist', is_default=True)
            return redirect(reverse('wishlist:wishlist_dashboard'))
    
    if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
        messages.info(request, "This product is already in your wishlist")
        return redirect(reverse('wishlist:wishlist_dashboard'))
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f"{product.title} added to {wishlist.name}")
        return redirect(reverse('wishlist:wishlist_dashboard'))
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect(request.META.get('HTTP_REFERER', 'product_detail'))

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    messages.success(request, "Item removed from wishlist")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('wishlist:wishlist_detail', wishlist_id=item.wishlist.id)

@login_required
def move_to_cart(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    product = item.product
    item.delete()
    return add_to_cart(request, product_id=product.id)

@login_required
def bulk_add_to_cart(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if not  wishlist.items == None:
        for item in wishlist.items.all():
            add_to_cart(request, product_id=item.product.id)
        messages.success(request, f"All items from {wishlist.name} added to cart")
    else:
        messages.error(request, "Error adding empty wishlist to cart!")
    return redirect(reverse('shop:cart'))

@login_required
def create_wishlist(request):
    if request.method == 'POST':
        form = CreateWishlistForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            messages.success(request, f"Wishlist '{wishlist.title}' created")
            return redirect('wishlist:wishlist_detail', wishlist_id=wishlist.id)
    return redirect('wishlist:wishlist_dashboard')

@login_required
def share_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if request.method == 'POST':
        form = ShareWishlistForm(request.POST)
        if form.is_valid():
            # In a real app, you'd send the email here
            share_url = request.build_absolute_uri(wishlist.get_absolute_url())
            messages.success(request, f"Share this link: {share_url}")
    return redirect('wishlist:wishlist_detail', wishlist_id=wishlist.id)

@login_required
def set_price_alert(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        desired_price = request.POST.get('desired_price')
        if desired_price:
            item.desired_price = desired_price
            item.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def delete_wishlist(request, wishlist_id):
    wishlist = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    if wishlist.is_default:
        messages.error(request, "Cannot delete default wishlist")
    else:
        wishlist.delete()
        messages.success(request, f"Wishlist '{wishlist.name}' deleted")
    return redirect('wishlist:wishlist_dashboard')

def send_price_alert_email(user, item):
    
    context = {
        'user': user,
        'item': item,
        'wishlist': item.wishlist,
        'site_name': settings.SITE_NAME
    }
    
    subject = f"Price Alert: {item.product.title} reached your desired price!"
    text_content = f"The price of {item.product.title} has dropped to ${item.product.price}."
    html_content = render_to_string('wishlist/email/price_alert.html', context)
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()