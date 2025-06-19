from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View, FormView
from django.conf import settings
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from datetime import time, datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Order, SavedPaymentMethod
from shop.models import Order as shop_order
import stripe
import json


# Create your views here.
    
class BillCheckoutView(View):
    template_name = 'payments/checkout.html'
    checkout_steps = ['Information', 'Payment', 'Review']
    
    def get(self, request, *args, **kwargs):
        # Get the plan and billing cycle from session or URL params
        plan = request.session.get('selected_plan', {})
        billing_cycle = request.session.get('billing_cycle', 'monthly')
        # if not plan:
        #     messages.warning(request, "Please opt selecting a plan first")
        #     return redirect(reverse_lazy('shop:cart'))
        order = Order.objects.all()
        context = {
            'checkout_steps': self.checkout_steps,
            # 'plan': plan,
            # 'billing_cycle': billing_cycle,
            # 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'order': order,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Determine which step we're processing
        step = request.POST.get('step', '1')
        
        if step == '1':
            return self.process_step1(request)
        elif step == '2':
            return self.process_step2(request)
        elif step == '3':
            return self.process_step3(request)
        else:
            return redirect(reverse('payments:checkout'))
    
    def process_step1(self, request):
        # Process customer information
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        opt_in_marketing = request.POST.get('optInMarketing') == 'on'
        
        # Validate data
        if not all([first_name, last_name, email]):
            messages.error(request, "Please fill in all required fields")
            return redirect(reverse('payments:checkout'))
        
        # Store in session
        request.session['customer_info'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'opt_in_marketing': opt_in_marketing,
        }
        
        # Redirect to payment step
        return redirect(reverse('payments:checkout') + '?step=2')
    
    def process_step2(self, request):
        # Process payment method selection
        payment_method = request.POST.get('payment_method', 'card')
        
        # Store in session
        request.session['payment_method'] = payment_method
        
        # For card payments, we'll process in step 3
        if payment_method == 'card':
            # Initialize Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            sh_ord = shop_order.objects.get(user=self.request.user, ordered=False)
            # Create payment intent (you might want to do this in step 3 instead)
            try:
                sh_ord = shop_order.objects.get(user=self.request.user, ordered=False)
                intent = stripe.PaymentIntent.create(
                    amount=int(sh_ord.get_total() * 100),  # in cents
                    currency='usd',
                    payment_method_types=['card'],
                    metadata={
                        'customer_email': request.session['customer_info']['email'],
                        'plan_id': request.session['selected_plan']['id'],
                    }
                )
                request.session['payment_intent_id'] = intent.id
                request.session['payment_intent_client_secret'] = intent.client_secret
            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {str(e)}")
                return redirect(reverse_lazy('payments:checkout') + '?step=2')
        
        # Redirect to review step
        return redirect(reverse_lazy('payments:checkout') + '?step=3')
    
    def process_step3(self, request):
        # Process final payment submission
        agreed_to_terms = request.POST.get('terms') == 'on'
        
        if not agreed_to_terms:
            messages.error(request, "You must agree to the terms and conditions")
            return redirect(reverse_lazy('payments:checkout') + '?step=3')
        
        payment_method = request.session.get('payment_method')
        if payment_method == 'card':
            return self.process_card_payment(request)
        elif payment_method == 'paypal':
            return self.process_paypal_payment(request)
        elif payment_method == 'bank':
            return self.process_bank_transfer(request)
        else:
            messages.error(request, "Invalid payment method")
            return redirect(reverse_lazy('payments:checkout') + '?step=2')
    
    def process_card_payment(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        payment_intent_id = request.session.get('payment_intent_id')
        
        try:
            # Confirm the payment (this would normally be done client-side with Stripe.js)
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Payment successful - create order record, etc.
                return self.handle_payment_success(request, intent)
            else:
                # Payment requires additional action (3D Secure, etc.)
                return JsonResponse({
                    'requires_action': True,
                    'client_secret': intent.client_secret
                })
        except stripe.error.StripeError as e:
            messages.error(request, f"Payment failed: {str(e)}")
            return redirect(reverse_lazy('payments:checkout') + '?step=3')
    
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
    
    def handle_payment_success(self, request, payment_result):
        customer_info = request.session.get('customer_info', {})
        selected_plan = request.session.get('selected_plan', {})
        sh_ord = shop_order.objects.get(user=self.request.user, ordered=False)        
        # Create order record
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_email=customer_info.get('email'),
            customer_first_name=customer_info.get('first_name'),
            customer_last_name=customer_info.get('last_name'),
            plan_name=selected_plan.get('name', ''),
            plan_id=selected_plan.get('id', ''),
            amount=selected_plan.get('amount'),
            tax_amount=selected_plan.get('tax_amount', 0),
            total_amount=selected_plan.get('total_amount'),
            billing_cycle=request.session.get('billing_cycle', ''),
            payment_method=request.session.get('payment_method'),
            payment_status='completed',
            payment_reference=payment_result.id,
            payment_details={
                'payment_result': payment_result,
                'stripe_payment_method_id': request.session.get('stripe_payment_method_id'),
            },
            opt_in_marketing=customer_info.get('opt_in_marketing', False)
        )
        
        # Save payment method if requested and user is authenticated
        save_payment = request.session.get('save_payment_method', False)
        if save_payment and request.user.is_authenticated:
            self.save_payment_method(request, payment_result)

        sh_ord.ordered = True
        # Clear session data
        for key in ['selected_plan', 'billing_cycle', 'customer_info', 'payment_method', 'save_payment_method']:
            if key in request.session:
                del request.session[key]
        
        return redirect(reverse_lazy('payments:payment-success') + f'?order_id={order.id}')
    
    def save_payment_method(self, request, payment_result):
        payment_method = request.session.get('payment_method')
        
        if payment_method == 'card':
            # Get payment method details from Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            pm = stripe.PaymentMethod.retrieve(payment_result.payment_method)
            
            # Create saved payment method
            SavedPaymentMethod.objects.create(
                user=request.user,
                payment_type='card',
                is_default=not SavedPaymentMethod.objects.filter(user=request.user).exists(),
                card_brand=pm.card.brand,
                card_last4=pm.card.last4,
                card_exp_month=pm.card.exp_month,
                card_exp_year=pm.card.exp_year,
                stripe_payment_method_id=pm.id
            )
        
        elif payment_method == 'paypal':
            # For PayPal, you would store the PayPal account details
            SavedPaymentMethod.objects.create(
                user=request.user,
                payment_type='paypal',
                is_default=not SavedPaymentMethod.objects.filter(user=request.user).exists(),
                paypal_email=payment_result.payer.email_address,
                paypal_payer_id=payment_result.payer.payer_id
            )    

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