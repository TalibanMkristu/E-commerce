from django.db import models

# Create your models here.
class Partners(models.Model):
    name = models.CharField(max_length=20)
    logo = models.ImageField(upload_to='media/partners')
    bio = models.TextField(null=True, blank=True)