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
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from .tokens import acount_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# Create your views here.
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and acount_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "ThankYou for confirming your registration. You can now Login to your account.")
        return redirect(reverse('users:login'))
    else:
        messages.error(request, "Activation Link is Invalid ! Try Again.")
    return redirect(reverse('base:index'))

def activateEmail(request, user, to_email):
    mail_subject = 'Activate Your Account'
    message = render_to_string("users/activate_account.html",
                               {
                                   'user': user.username,
                                   'domain':get_current_site(request).domain,
                                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                   'token': acount_activation_token.make_token(user),
                                   'protocol': 'https' if request.is_secure() else 'http'
                               }
                               )
    email = EmailMessage(mail_subject, message, to={to_email})
    email.content_subtype = 'html'  # This is the key line that makes it HTML
    if email.send():
        messages.success(request, f"Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on\
                        received activation link to confirm and complet the registration.\
                        <b>NOTE:</b> check on your spam folder.")
    else:
        messages.error(request, f"Absurd\
        Problem sending email to {to_email} , check if you typed it correctly.")

class RegisterView(FormView):
    template_name = 'users/register_login.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        activateEmail(self.request, user, form.cleaned_data.get('email'))
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
