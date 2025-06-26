from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_dashboard, name='wishlist_dashboard'),
    path('wishlists/<str:wishlist_id>/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlists/add/<str:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlists/remove/<str:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlists/move-to-cart/<str:item_id>/', views.move_to_cart, name='move_to_cart'),
    path('wishlists/bulk-add/<str:wishlist_id>/', views.bulk_add_to_cart, name='bulk_add_to_cart'),
    path('wishlists/create/', views.create_wishlist, name='create_wishlist'),
    path('wishlists/share/<str:wishlist_id>/', views.share_wishlist, name='share_wishlist'),
    path('wishlists/set-alert/<str:item_id>/', views.set_price_alert, name='set_price_alert'),
    path('shared/<uuid:token>/', views.shared_wishlist, name='shared_wishlist'),
    path('wishlists/delete/<str:wishlist_id>/', views.delete_wishlist, name='delete_wishlist'),    
]