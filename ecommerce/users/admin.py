from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# Register your models here.

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     fieldsets = UserAdmin.fieldsets + (
#         ("Additional Info", {
#             "fields" : ("avatar", "phone", "is_email_verified", "last_seen")
#         }),
#     )

admin.site.register(CustomUser)