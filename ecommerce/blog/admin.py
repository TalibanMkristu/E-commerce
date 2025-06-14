from django.contrib import admin
from .models import Category, Blog

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('name',)  }
    list_display = ('name', 'slug')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ('heading',)  }    
    list_display = ('category', 'heading', 'description', 'posted_at', 'published')
    list_filter = ('category',)