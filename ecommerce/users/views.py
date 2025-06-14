from django.shortcuts import render, redirect
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib import messages
from .forms import (CustomUserCreationForm, 
                    PasswordChangeForm, 
                    CustomPasswordResetForm,
                    CustomAuthForm, 
                    ProfileUpdateForm,
                    )
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
# Create your views here.


class RegisterView(FormView):
    template_name = 'users/register_login.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Account created successfully for {self.object.username} ! ")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field.capitalize()}: {error}')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'register'
        return context
    
class LoginView(FormView):
    template_name = "users/register_login.html"
    form_class = CustomAuthForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('base:index')
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(0)

        login(self.request, form.get_user())
        messages.success(self.request, f'Welcome back {form.get_user().username} !')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid Credentials !")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'login'
        return context

class CustomLogoutView(LogoutView):
    
    def get_next_page(self):
        messages.info(self.request, 'You have been logged out successfully!')
        return reverse_lazy("base:index") 
    
class PasswordReset(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    
    def get_success_url(self):
        return redirect('users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = 'Reset password'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset email sent to your inbox. Remember to check spam')
        return super().form_valid(form)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'users/profile.html'
    success_url = '/profile/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page']= 'Profile'
        return context
    
    def get_object(self, queryset = None):
        return self.request.user

    def form_valid(self, form):
        response =  super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully !')
        return response

class PasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'users/password_change.html'
    success_message = 'Password has been changed successfully !'
    success_url = '/profile/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page']= 'change  password'
        return context
