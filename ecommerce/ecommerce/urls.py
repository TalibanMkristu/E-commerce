"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls', namespace='base')),
    path('auth/', include('users.urls', namespace='users')),
    path('about/', include('about.urls', namespace='about')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('shop/', include('shop.urls', namespace='shop')),
    path('contacts/', include('contacts.urls', namespace='contacts')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('privacy-terms/', include('policy.urls', namespace="policy")),
    path('news-letter/', include('newsletter.urls', namespace='newsletter')),
    path('wishlist/', include('wishlist.urls', namespace='wishlist')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)