from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.BillCheckoutView.as_view(), name="checkout"),
    path('payment-success/', views.PaymentSuccessView.as_view(), name="payment-success"),
    path('payment-dashboard/', views.PaymentsDashboard.as_view(), name="payment-dashboard"),
    path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('get-saved-cards/',views.get_saved_cards, name="get-saved-cards" ),
    path('use_saved_card/', views.use_saved_card, name="use-saved-card"),

]