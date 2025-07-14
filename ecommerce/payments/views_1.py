# payments/views.py
import logging
import json
import stripe
import stripe.error
from datetime import time, datetime
from django.conf import settings
from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, SavedPaymentMethod
from shop.models import Order as ShopOrder
from django.views.decorators.http import require_POST

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY

class BillCheckoutView(LoginRequiredMixin, View):
    template_name = 'payments/checkout.html'
    checkout_steps = ['Information', 'Payment', 'Review']
    
    def get(self, request, *args, **kwargs):
        try:
            # Get current shop order
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            
            context = {
                'checkout_steps': self.checkout_steps,
                'shop_order': shop_order,
                'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                'current_step': request.GET.get('step', '1'),
            }
            
            # Add customer info if available
            if 'customer_info' in request.session:
                context.update(request.session['customer_info'])
                
            return render(request, self.template_name, context)
            
        except ShopOrder.DoesNotExist:
            messages.error(request, "No active order found")
            return redirect(reverse('shop:cart'))
        except Exception as e:
            messages.error(request, f"Error loading checkout: {str(e)}")
            return redirect(reverse('shop:cart'))
    
    def post(self, request, *args, **kwargs):
        # Process AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax_request(request)
        
        # Process form submissions
        step = request.POST.get('step', '1')
                
        if step == '1':
            return self.process_step1(request)
        elif step == '2':
            return self.process_step2(request)
        elif step == '3':
            return self.process_step3(request)
        else:
            messages.error(request, "Invalid checkout step")
            return redirect(reverse('payments:checkout'))
    def handle_ajax_request(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')

            customer = data.get('customer')
            if customer:
                request.session['customer_info'] = {
                    'first_name': customer.get('firstName', '').strip(),
                    'last_name': customer.get('lastName', '').strip(),
                    'email': customer.get('email', '').strip().lower(),
                    'opt_in_marketing': customer.get('optInMarketing', False)
                }
                request.session.modified = True
            
            if action == 'create_payment_intent':
                return self.create_payment_intent(request)
            elif action == 'confirm_payment':
                return self.confirm_payment(request, data)
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def process_step1(self, request):
        try:
            customer_info = {
                'first_name': request.POST.get('first-name', '').strip(),
                'last_name': request.POST.get('last-name', '').strip(),
                'email': request.POST.get('email', '').strip().lower(),
                'opt_in_marketing': request.POST.get('optInMarketing') == 'on'
            }
            # Validate data
            if not all([customer_info['first_name'], customer_info['last_name'], customer_info['email']]):
                messages.error(request, "Please fill in all required fields")
                return redirect(reverse('payments:checkout'))
                
            if '@' not in customer_info['email']:
                messages.error(request, "Please enter a valid email address")
                return redirect(reverse('payments:checkout'))
            
            # Store in session
            request.session['customer_info'] = customer_info
            request.session.modified = True
            
            return redirect(reverse('payments:checkout') + '?step=2')
            
        except Exception as e:
            messages.error(request, f"Error processing information: {str(e)}")
            return redirect(reverse('payments:checkout'))
    
    def process_step2(self, request):
        try:
            payment_method = request.POST.get('payment_method', 'card')
            valid_methods = ['card', 'paypal', 'bank']
            if payment_method not in valid_methods:
                messages.error(request, "Invalid payment method")
                return redirect(reverse('payments:checkout') + '?step=2')
            
            request.session['payment_method'] = payment_method
            request.session.modified = True
            
            return redirect(reverse('payments:checkout') + '?step=3')
            
        except Exception as e:
            messages.error(request, f"Error selecting payment method: {str(e)}")
            return redirect(reverse('payments:checkout') + '?step=2')
    
    def process_step3(self, request):
        try:
            if 'customer_info' not in request.session or 'payment_method' not in request.session:
                messages.error(request, "Missing checkout information")
                return redirect(reverse('payments:checkout'))
                
            if request.POST.get('terms') != 'on':
                messages.error(request, "You must agree to the terms and conditions")
                return redirect(reverse('payments:checkout') + '?step=3')
                        
            if request.session['payment_method'] == 'card':
                if 'payment_intent_id' not in request.session:
                    messages.error(request, "Payment not initialized")
                    return redirect(reverse('payments:checkout') + '?step=2')
                
                intent = stripe.PaymentIntent.retrieve(request.session['payment_intent_id'])
                if intent.status != 'succeeded':
                    messages.error(request, "Payment not completed")
                    return redirect(reverse('payments:checkout') + '?step=2')
                
                return self.handle_payment_success(request, intent, ajax=True)
                
            elif request.session['payment_method'] == 'paypal':
                return self.process_paypal_payment(request)
                
            elif request.session['payment_method'] == 'bank':
                return self.process_bank_transfer(request)
                
        except stripe.error.StripeError as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect(reverse('payments:checkout') + '?step=2')
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect(reverse('payments:checkout'))
    def create_payment_intent(self, request):
        try:
            if 'customer_info' not in request.session:
                return JsonResponse({'error': 'Customer information missing'}, status=400)
                
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            # Create or update payment intent
            if 'payment_intent_id' in request.session:
                intent = stripe.PaymentIntent.modify(
                    request.session['payment_intent_id'],
                    amount=int(shop_order.total * 100),
                    currency='usd',
                    metadata={
                        'user_id': request.user.id,
                        'order_id': shop_order.id,
                        'customer_email': request.session['customer_info']['email']
                    }
                )
            else:
                intent = stripe.PaymentIntent.create(
                    amount=int(shop_order.total * 100),
                    currency='usd',
                    payment_method_types=['card'],
                    metadata={
                        'user_id': request.user.id,
                        'order_id': shop_order.id,
                        'customer_email': request.session['customer_info']['email']
                    },
                    receipt_email=request.session['customer_info']['email']
                )
            
            request.session['payment_intent_id'] = intent.id
            request.session['payment_intent_client_secret'] = intent.client_secret
            request.session.modified = True
            
            return JsonResponse({
                'client_secret': intent.client_secret,
                'paymentIntentId': intent.id
            })
            
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def confirm_payment(self, request, data):
        try:
            payment_intent_id = data.get('paymentIntentId')
            if payment_intent_id != request.session.get('payment_intent_id'):
                return JsonResponse({'error': 'Invalid payment intent'}, status=400)
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                return self.handle_payment_success(request, intent, ajax=True)
                
            elif intent.status == 'requires_action':
                return JsonResponse({
                    'requiresAction': True,
                    'clientSecret': intent.client_secret
                })
                
            elif intent.status == 'requires_payment_method':
                return JsonResponse({
                    'error': 'Payment failed. Please try another payment method.'
                }, status=400)
                
            else:
                return JsonResponse({
                    'error': f'Unexpected payment status: {intent.status}'
                }, status=400)
                
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def handle_payment_success(self, request, payment_intent, ajax=False):
        try:
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            customer_info = request.session.get('customer_info', {})
            existing_order = Order.objects.filter(stripe_payment_intent_id = payment_intent.id).first()
            # avoid duplicates
            # if existing_order:
            #     return JsonResponse({'success': True, 'redirectUrl': reverse('payments:payment-success') + f'?order_id={existing_order.id}'})            
            # Create payment order
            order = Order.objects.create(
                user=request.user,
                shop_order=shop_order,
                customer_email=customer_info.get('email'),
                customer_first_name=customer_info.get('first_name'),
                customer_last_name=customer_info.get('last_name'),
                amount=shop_order.total,
                total_amount=shop_order.total,
                payment_method=request.session.get('payment_method', 'card'),
                payment_status='completed',
                payment_reference=payment_intent.id,
                stripe_payment_intent_id=payment_intent.id,
                stripe_client_secret=payment_intent.client_secret,
                payment_details={
                    'payment_intent': payment_intent.id,
                    'amount_received': payment_intent.amount_received,
                    'payment_method': payment_intent.payment_method.id if payment_intent.payment_method else None,
                },
                opt_in_marketing=customer_info.get('opt_in_marketing', False)
            )
            
            # Mark shop order as paid
            shop_order.ordered = True
            shop_order.save()
            
            # Save payment method if requested
            if request.POST.get('save_payment_method') == 'true':
                self.save_payment_method(request, payment_intent)
            
            # Clear session
            for key in ['payment_intent_id', 'payment_intent_client_secret', 
                       'payment_method', 'customer_info']:
                if key in request.session:
                    del request.session[key]
            
            if ajax:
                return JsonResponse({
                    'success': True,
                    'redirectUrl': reverse('payments:payment-success') + f'?order_id={order.id}'
                })
            
            return redirect(reverse('payments:payment-success') + f'?order_id={order.id}')
            
        except Exception as e:
            if ajax:
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, f"Error completing order: {str(e)}")
            return redirect(reverse('payments:checkout'))
    
    def save_payment_method(self, request, payment_intent):
        try:
            if request.session.get('payment_method') == 'card' and payment_intent.payment_method:
                payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
                
                SavedPaymentMethod.objects.update_or_create(
                    user=request.user,
                    stripe_payment_method_id=payment_method.id,
                    defaults={
                        'payment_type': 'card',
                        'is_default': not SavedPaymentMethod.objects.filter(user=request.user).exists(),
                        'card_brand': payment_method.card.brand,
                        'card_last4': payment_method.card.last4,
                        'card_exp_month': payment_method.card.exp_month,
                        'card_exp_year': payment_method.card.exp_year,
                    }
                )
            SavedPaymentMethod.update_from_stripe()
                
        except Exception as e:
            logger.error(f"Error saving payment method: {str(e)}")

    def process_paypal_payment(self, request):
        # Implement PayPal integration here
        # This would typically redirect to PayPal for approval
        # Then have a return URL that processes the completed payment
        
        # For now, just simulate success
        return self.handle_payment_success(request, {'id': 'simulated_paypal_id'})
    
    def process_bank_transfer(self, request):
        # Generate bank transfer reference
        reference = f"BANK-{request.session['customer_info']['email']}-{int(time.time())}"
        
        # In a real implementation, you would:
        # 1. Create an order record with "pending" status
        # 2. Send email with bank details
        # 3. Redirect to instructions page
        
        return redirect(reverse('payments:bank-transfer-instructions') + f'?reference={reference}')


class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        # Verify the payment with Stripe
        # Retrieve order details
        context = {
            'session_id': session_id,
            # other order details
        }
        return render(request, 'payments/payments_success.html', context)

class PaymentsDashboard(TemplateView):
    template_name = 'payments/subscriptions.html'


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_intent_failed(payment_intent)
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object
        handle_payment_method_attached(payment_method)
    # ... handle other event types

    return HttpResponse(status=200)

def handle_payment_intent_succeeded(payment_intent):
    # Find or create order
    order, created = Order.objects.get_or_create(
        payment_reference=payment_intent.id,
        defaults={
            'payment_status': 'pending',
            'payment_method': 'card',
            'payment_details': {
                'payment_intent': payment_intent.id,
                'amount_received': payment_intent.amount_received,
                'charges': payment_intent.charges.data if hasattr(payment_intent, 'charges') else None,
            }
        }
    )
    
    if not created:
        order.payment_status = 'completed'
        order.payment_details.update({
            'amount_received': payment_intent.amount_received,
            'charges': payment_intent.charges.data if hasattr(payment_intent, 'charges') else None,
        })
        order.save()
    
    # Additional logic: send confirmation email, update user subscription, etc.

def handle_payment_intent_failed(payment_intent):
    order = Order.objects.filter(payment_reference=payment_intent.id).first()
    if order:
        order.payment_status = 'failed'
        order.payment_details.update({
            'last_payment_error': payment_intent.last_payment_error,
        })
        order.save()

def handle_payment_method_attached(payment_method):
    # This would be called when a payment method is attached to a customer
    # You could update your SavedPaymentMethod records here
    pass


@require_POST
@login_required
def save_card(request):
    try:
        data = json.loads(request.body)
        
        # Validate expiry
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        if not (1 <= data['exp_month'] <= 12):
            raise ValueError("Invalid expiration month")
            
        if data['exp_year'] < current_year or \
           (data['exp_year'] == current_year and data['exp_month'] < current_month):
            raise ValueError("Card has expired")
        
        # Create payment method
        method = SavedPaymentMethod.objects.create(
            user=request.user,
            payment_type='card',
            card_brand=data.get('brand', '').lower(),
            card_number=data['number'],
            card_name=data.get('name', ''),
            card_last4=data['number'][-4:],
            card_exp_month=data['exp_month'],
            card_exp_year=data['exp_year'],
            stripe_payment_method_id=data.get('token', '')
        )
        
        return JsonResponse({
            'id': method.id,
            'brand': method.card_brand,
            'last4': method.card_last4,
            'expiry': method.formatted_expiry,
            'is_default': method.is_default
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
def get_saved_cards(request):
    cards = SavedPaymentMethod.objects.filter(
        user=request.user, 
        payment_type='card'
    ).values('id', 'card_brand', 'card_last4')
    
    return JsonResponse(list(cards), safe=False)

@login_required
@require_POST
def use_saved_card(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        # Get the saved card
        card = SavedPaymentMethod.objects.get(
            id=card_id,
            user=request.user
        )
        shop_order = ShopOrder.objects.get(ordered = False, user = request.user)
        # Create payment intent with saved card
        intent = stripe.PaymentIntent.create(
            amount=shop_order.total,  # Replace with actual amount
            currency='usd',
            customer=request.user.stripe_customer_id,  # Assuming you store this
            payment_method=card.stripe_payment_method_id,
            confirm=True,
            off_session=True  # Customer isn't present
        )
        
        if intent.status == 'requires_action':
            return JsonResponse({
                'requires_action': True,
                'client_secret': intent.client_secret
            })
            
        return JsonResponse({
            'status': 'succeeded',
            'session_id': intent.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)    