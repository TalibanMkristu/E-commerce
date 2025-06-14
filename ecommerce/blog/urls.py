from django.urls import path
from . import views
app_name = 'blog'

urlpatterns = [
    path('', views.BlogView.as_view(), name="blog"), 
    path('blog-single/<slug:slug>/', views.SingleBlogView.as_view(), name="blog-single")
]