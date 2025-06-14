from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

def userAvatarPath(instance, filename):
    return f'media/profilePicture/user_{instance.id}/{filename}'

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to=userAvatarPath, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    REQUIRED_FIELDS= ['first_name', 'last_name', 'email', ]
    # USERNAME_FIELD  = 'username'
    def __str__(self):
        return self.username