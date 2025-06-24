from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.ShopView.as_view(), name="shop"),
    path('cart/', views.CartView.as_view(), name="cart"),
    path('add-to-cart/<slug:slug>/', views.AddToCartView.as_view(), name="add-to-cart"),
    path('remove-from-cart/<slug:slug>/', views.RemoveFromCartView.as_view(), name="remove-from-cart"),
    path('remove-item-from-cart/<slug:slug>/', views.RemoveSingleItemFromCartView.as_view(), name="remove-item-from-cart"),
    path('check-out/', views.CheckOutView.as_view(), name="check-out"),
    path('wish-list/', views.WishListView.as_view(), name="wish-list"),
    path('product-single/<slug:slug>/', views.SingleProductView.as_view(), name="product-single"),
    path('add-wishlist/<slug:slug>/', views.AddToWishlist.as_view(), name="add-wish-list"),
    path('remove-wishlist/<slug:slug>/', views.RemoveFromWishlist.as_view(), name="remove-wish-list"),
]