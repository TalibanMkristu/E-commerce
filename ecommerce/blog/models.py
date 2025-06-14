from django.db import models
from datetime import datetime
from django.urls import reverse
from django.utils.text import slugify
import itertools

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = orig = slugify(self.name)
            for x in itertools.count(1):
                if not Blog.objects.filter(slug = self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig, x)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name    
    

class Blog(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    heading = models.CharField(max_length=200)
    background_image = models.ImageField(null=True, upload_to='media/images')
    description = models.CharField(max_length=100000)
    slug = models.SlugField(unique=True, null=True, blank=True)
    posted_at = models.DateTimeField(default=datetime.now)
    published = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('blog:blog-single', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = orig = slugify(self.heading)
            for x in itertools.count(1):
                if not Blog.objects.filter(slug = self.slug).exists():
                    break
                self.slug = "%s-%d" % (orig, x)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.heading