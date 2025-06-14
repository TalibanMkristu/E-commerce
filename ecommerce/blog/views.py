from django.shortcuts import render, redirect
from django.views.generic import (TemplateView, ListView, DetailView)
from .models import Blog, Category

# Create your views here.
class BlogView(ListView):
    Model = Blog
    template_name = 'blog/blog.html'
    paginate_by = 20
    context_object_name = 'blogs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'tracy-blog' 
        context['page_name'] = 'my-blog' 
        context['categories'] = Category.objects.all()
        # context['recent_blogs'] = Blog.objects.exclude(id = self.object.id).order_by('-posted_at')[:3]
        # listView lacks self.object
        return context
    
    def get_queryset(self):
        response = Blog.objects.filter(published=True).order_by('-posted_at')
        return response
    
class SingleBlogView(DetailView):
    model = Blog
    template_name = 'blog/blog_single.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'blog'
        categories = Category.objects.all()
        current_blog = context['blog']
        related_blogs = Blog.objects.filter(
            category = current_blog.category,
            published = True
        ).exclude(
            id = current_blog.id
        ).order_by(
            '-posted_at'
        )[:3]
        context['related_blogs'] = related_blogs
        context['categories'] = categories
        return context