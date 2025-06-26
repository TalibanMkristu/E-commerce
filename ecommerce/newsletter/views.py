from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import NewsletterForm, NewsletterBroadcastForm
from .models import Subscriber, Newsletter
import csv

def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            if created:
                subscriber.send_confirmation_email()
                messages.success(request, f'Confirmation email sent to {email}. Please check your inbox.')
            else:
                messages.info(request, f'{email} is already subscribed.')
            return redirect('newsletter')
        else:
            messages.error(request, 'Please enter a valid email address.')
    else:
        form = NewsletterForm()
    
    return render(request, 'newsletter/sign_up.html', {'form': form})

def confirm_subscription(request, token):
    try:
        subscriber = Subscriber.objects.get(confirmation_token=token)
        subscriber.is_confirmed = True
        subscriber.save()
        messages.success(request, 'Your subscription has been confirmed!')
    except Subscriber.DoesNotExist:
        messages.error(request, 'Invalid confirmation link.')
    return redirect('newsletter')

def export_subscribers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Date Subscribed', 'Confirmed'])
    
    subscribers = Subscriber.objects.all().order_by('-date_subscribed')
    for sub in subscribers:
        writer.writerow([sub.email, sub.date_subscribed, sub.is_confirmed])
    
    return response

def broadcast_newsletter(request):
    if not request.user.is_staff:
        return redirect('home')
    
    if request.method == 'POST':
        form = NewsletterBroadcastForm(request.POST)
        if form.is_valid():
            newsletter = form.save()
            newsletter.send_to_subscribers()
            messages.success(request, 'Newsletter has been sent to all confirmed subscribers!')
            return redirect('broadcast')
    else:
        form = NewsletterBroadcastForm()
    
    return render(request, 'newsletter/broadcast.html', {'form': form})