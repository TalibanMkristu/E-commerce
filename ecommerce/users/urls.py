from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.CustomLogoutView.as_view(), name="logout"),
    path('password-reset/', views.PasswordReset.as_view(), name="password_reset"),
    path('change-password/', views.PasswordChangeView.as_view(), name="change-password"),
    path('resst-password/', views.PasswordResetView.as_view(), name="reset-password"),
    path('profile-update/', views.ProfileUpdateView.as_view(), name="profile-update"),

]

