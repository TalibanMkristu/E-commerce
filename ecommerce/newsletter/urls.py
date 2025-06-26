from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('', views.newsletter_signup, name='newsletter'),
    path('newsletter/confirm/<uuid:token>/', views.confirm_subscription, name='confirm_subscription'),
    path('newsletter/export/', views.export_subscribers_csv, name='export_subscribers'),
    path('newsletter/broadcast/', views.broadcast_newsletter, name='broadcast'),
]