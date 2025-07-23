# payments/views.py
import os
import logging
import json
import stripe
from datetime import datetime
from django.conf import settings
from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, SavedPaymentMethod
from shop.models import Order as ShopOrder
from django.views.decorators.http import require_POST
from django.db.models import Q
# logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def setupLogger(log_level=logging.DEBUG, log_file=None):
    """Creating logger"""
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    if logger.handlers:
        """Prevents returning handlers multiple times"""
        return logger
    """Desired log formatting"""
    formatter = logging.Formatter(
        "[ [%(asctime)s] [%(name)s] %(levelname)s >> %(message)s ]",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    """Creating console handler"""
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    """File handler if specified in log_file else defaulting to None"""
    if log_file:
        """Create a directory if None for logs"""
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setupLogger(log_file='EcommerceLogs/payments.log')



class BillCheckoutView(LoginRequiredMixin, View):
    template_name = 'payments/checkout.html'
    checkout_steps = ['Information', 'Payment', 'Review']
    
    def get(self, request, *args, **kwargs):
        try:
            logger.info('---- Rendering ecommerce page -----')
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            
            context = {
                'checkout_steps': self.checkout_steps,
                'shop_order': shop_order,
                'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
                'current_step': request.GET.get('step', '1'),
            }
            
            if 'customer_info' in request.session:
                context.update(request.session['customer_info'])
                
            return render(request, self.template_name, context)
            
        except ShopOrder.DoesNotExist:
            messages.error(request, "No active order found")
            return redirect(reverse('shop:cart'))
        except Exception as e:
            logger.error(f"Error loading checkout: {str(e)}")
            messages.error(request, "Error loading checkout page")
            return redirect(reverse('shop:cart'))
    
    def post(self, request, *args, **kwargs):
        try:
            # logger.info('Rguest.body: ',request.body)
            logger.info(f'Request.headers: {request.headers}')
            logger.info(f'Request content type: {request.content_type}')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                logger.info('---- Starting processing ajax post payment request ----')
                data = json.loads(request.body)
                logger.info(f'Parsed Ajax data: {data}')
                action = data.get('action')
                
                if action == 'create_payment_intent':
                    return self.create_payment_intent(request, data)
                elif action == 'confirm_payment':
                    logger.info(f'----Starting to confirm payment inten ----')
                    return self.confirm_payment(request, data)
                elif action == 'validate_step_1':
                    logger.info('---Seever Validating step 1')
                    return self.process_step1(request, data)
                elif action == 'validate_step_2':
                    logger.info(f'---Starting to Validate step 2----')
                    return self.process_step2(request, data)
                else:
                    return JsonResponse({'error': 'Invalid action'}, status=400)
            else:
                logger.warning('--Ajax processing failed---')
                logger.warning('Processing non ajax request ')
                return JsonResponse({'failed': 'ajax-failed'})
                
        except json.JSONDecodeError as e:
            logger.error(f'Json decoder error: {e}')
            return JsonResponse({'error': 'Invalid JSON', 'success':'false'}, status=400)
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            return JsonResponse({'error': 'Server error', 'success': 'false'}, status=500)
    
    def process_step1(self, request, data=None, *a,**k):
        try:
            if data == None:
                data = json.loads(request.body)

            customer_data = data.get('customer', {})
            customer_info = {
                'first_name': customer_data.get('firstName', '').strip(),
                'last_name': customer_data.get('lastName', '').strip(),
                'email': customer_data.get('email', '').strip().lower(),
                'opt_in_marketing': customer_data.get('optInMarketing', False)
            }
            logger.info( dict(customer_info))

            #validation of the fields not to be null
            if not all([customer_info['first_name'], customer_info['last_name'], customer_info['email']]):
                messages.error(request, "Please fill in all required fields")
                return redirect(reverse('payments:checkout'))
                
            if '@' not in customer_info['email']:
                messages.error(request, "Please enter a valid email address")
                return redirect(reverse('payments:checkout'))
            
            request.session['customer_info'] = customer_info
            request.session.modified = True
            logger.info(f'Request.session: {request.session.get('customer_info')}')
            logger.info('---Processed step 1 succesfully ---')
            
            return redirect(reverse('payments:checkout') + '?step=2')
            
        except Exception as e:
            logger.error(f"Error processing step 1: {str(e)}")
            messages.error(request, "Error processing your information")
            return redirect(reverse('payments:checkout'))
    
    def process_step2(self, request, data=None, *a, **k):
        try:
            if data == None:
                data = json.loads(request.body)
            logger.info(f'Received paymnet method: {data.get('payment_method')}')
            payment_method = data.get('payment_method', 'card')
            valid_methods = ['card', 'paypal', 'bank']
            if payment_method not in valid_methods:
                messages.error(request, "Invalid payment method")
                return redirect(reverse('payments:checkout') + '?step=2')
            
            logger.info(f'Payment method: {payment_method}')
            request.session['payment_method'] = payment_method
            request.session.modified = True
            
            return redirect(reverse('payments:checkout') + '?step=3')
            
        except Exception as e:
            logger.error(f"Error processing step 2: {str(e)}")
            messages.error(request, "Error selecting payment method")
            return redirect(reverse('payments:checkout') + '?step=2')
    
    # def process_step3(self, request):
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
                
                return self.handle_payment_success(request, intent)
                
            elif request.session['payment_method'] == 'paypal':
                return self.process_paypal_payment(request)
                
            elif request.session['payment_method'] == 'bank':
                return self.process_bank_transfer(request)
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error in step 3: {str(e)}")
            messages.error(request, f"Payment error: {str(e.user_message)}")
            return redirect(reverse('payments:checkout') + '?step=2')
        except Exception as e:
            logger.error(f"Error processing step 3: {str(e)}")
            messages.error(request, "Error processing payment")
            return redirect(reverse('payments:checkout'))
    
    def create_payment_intent(self, request, data=None):
        try:
            if data == None:
                data = json.loads(request.body)
            if 'customer_info' not in request.session:
                return JsonResponse({'error': 'Customer information missing'}, status=400)
                
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            amount = int(shop_order.total * 100)
            payment_method_id = data.get('payment_method_id')
            
            # Check if we have an existing payment intent
            payment_intent_id = request.session.get('payment_intent_id')
            
            if payment_intent_id:
                logger.info(f'-----Using cached payment intent (existing instance)----')
                # Retrieve existing intent first
                existing_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                logger.info(f'Retrieved existing cient intent id: {existing_intent}')
                
                # Only modify if in a modifiable state
                if existing_intent.status in ['requires_payment_method', 'requires_confirmation', 'requires_action']:
                    # Check if amount changed
                    if existing_intent.amount != amount:
                        intent = stripe.PaymentIntent.modify(
                            payment_intent_id,
                            amount=amount,
                            metadata={
                                'user_id': request.user.id,
                                'order_id': shop_order.id,
                                'customer_email': request.session['customer_info']['email']
                            }
                        )
                    else:
                        intent = existing_intent
                        confirm_intent = stripe.PaymentIntent.confirm(
                            intent.id,
                            # return_url=f'http://{request.get_host()}/payments/'
                        )
                else:
                    # Create new intent if existing one is in terminal state
                    intent = stripe.PaymentIntent.create(
                        amount=amount,
                        currency='usd',
                        payment_method_types=['card'],
                        metadata={
                            'user_id': request.user.id,
                            'order_id': shop_order.id,
                            'customer_email': request.session['customer_info']['email']
                        },
                        receipt_email=request.session['customer_info']['email']
                    )
            else:
                # Create new intent if none exists
                logger.info(f'------Creating new payment intent----')
                # intent = self._create_new_intent(request, amount, payment_method_id, shop_order, confirm=True)
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    payment_method_types=['card'],
                    payment_method=payment_method_id,
                    # confirm=True,
                    # confirmation_method='automatic',
                    metadata={
                        'user_id': request.user.id,
                        'order_id': shop_order.id,
                        'customer_email': request.session['customer_info']['email']
                    },
                    receipt_email=request.session['customer_info']['email'],
                )

                logger.info(f'Created intent: {intent}')
            request.session['payment_intent_id'] = intent.id
            request.session['payment_intent_client_secret'] = intent.client_secret
            request.session.modified = True

            logger.info(f'Printing curent request.sesion: {list(request.session.keys())}')
            logger.info(f'----Payment intent created successfully----')
            logger.info(f'----Sending cl_secret and intent id to fronted-----{intent.client_secret}, {intent.id}')
            return JsonResponse({
                'client_secret': intent.client_secret,
                'paymentIntentId': intent.id
            })
            
        except ShopOrder.DoesNotExist:
            return JsonResponse({'error': 'No active order found'}, status=400)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            return JsonResponse({'error': str(e.user_message)}, status=400)
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            return JsonResponse({'error': 'System error'}, status=500)
        
    def _create_new_intent(self, request, amount, payment_method_id, shop_order, confirm=False):
        """Helper method to create new payment intent"""
        intent_params = {
            'amount': amount,
            'currency': 'usd',
            'payment_method': payment_method_id,
            'metadata': {
                'user_id': request.user.id,
                'order_id': shop_order.id,
                'customer_email': request.session['customer_info']['email']
            },
            'receipt_email': request.session['customer_info']['email'],
            'confirmation_method': 'manual' if confirm else 'automatic',
            'confirm': confirm
        }
        
        if not confirm:
            intent_params['payment_method_types'] = ['card']
        
        intent = stripe.PaymentIntent.create(**intent_params)
        logger.info(f'Created new intent: {intent.id} (status: {intent.status})')
        return intent
    
    def confirm_payment(self, request, data=None):
        try:
            if data == None:
                data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            if not payment_intent_id or payment_intent_id != request.session.get('payment_intent_id'):
                return JsonResponse({'error': 'Invalid payment intent'}, status=400)
            
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Verify the amount matches
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            expected_amount = int(shop_order.total * 100)
            logger.info(f'---Confirming amount matches from fronted ----')
            if intent.amount != expected_amount:
                return JsonResponse({
                    'error': f'Amount mismatch. Expected {expected_amount}, got {intent.amount}'
                }, status=400)
                
            if intent.status == 'succeeded':
                logger.info(f'---Payment intent status successfull ---')
                logger.info(f'-----Redirecting to handle payment sucess instance----')
                return self.handle_payment_success(request, intent, data)
                
            elif intent.status == 'requires_action':
                return JsonResponse({
                    'requiresAction': True,
                    'clientSecret': intent.client_secret,
                    'paymentMethod': intent.payment_method
                })
                
            elif intent.status == 'requires_payment_method':
                logger.error(f'Payment failed for intent {intent.id}: {intent.last_payment_error}')
                return JsonResponse({
                    'error': intent.last_payment_error.message if intent.last_payment_error 
                            else 'Payment failed. Please try another payment method.'
                }, status=400)
                
            else:
                logger.warning(f'Unexpected payment status for intent {intent.id}: {intent.status}')
                return JsonResponse({
                    'error': f'Unexpected payment status: {intent.status}'
                }, status=400)
                
        except stripe.error.StripeError as e:
            logger.error(f'Stripe error in confirm_payment: {str(e)}')
            return JsonResponse({'error': str(e.user_message)}, status=400)
        except Exception as e:
            logger.error(f'Error in confirm_payment: {str(e)}')
            return JsonResponse({'error': 'Payment confirmation failed'}, status=500)
    
    def handle_payment_success(self, request, payment_intent, data=None):
        try:
            if data == None:
                data = json.loads(request.body)

            #save the model instance field
            # Order.update_from_stripe(payment_intent)
            # SavedPaymentMethod.update_from_stripe(payment_intent)

            logger.info(f'---handling payment success----')
            shop_order = ShopOrder.objects.get(user=request.user, ordered=False)
            customer_info = request.session.get('customer_info', {})
            
            # Check for existing order to prevent duplicates
            existing_order = Order.objects.filter(
                stripe_payment_intent_id=payment_intent.id,
                user=request.user
            ).first()

            logger.info(f'Existing order: {existing_order}')

            if existing_order:
                logger.info(f'Handling payment success of existing order')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    success_url = reverse('payments:payment-success') + \
                        f'?order_id = {existing_order.id}&payment_intent_id={payment_intent.id}'
                    return JsonResponse({
                        'success': True,
                        'redirectUrl': success_url,
                    })
                
                return redirect(reverse(success_url))
            logger.info('No existing ordders found')

            # Create new payment order
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
                    'payment_method': payment_intent.payment_method if isinstance(payment_intent.payment_method, str) 
                                      else payment_intent.payment_method.id if payment_intent.payment_method 
                                      else None,
                    #card info
                    # 'brand': payment_intent.payment_method.card.brand, 
                    # 'last4': payment_intent.payment_method.card.last4,  
                    # 'exp_month': payment_intent.payment_method.card.exp_month,
                    # 'exp_year': payment_intent.payment_method.card.exp_year,
                    # 'country': payment_intent.payment_method.card.country,  
                    # 'funding': payment_intent.payment_method.card.funding  
                },
                opt_in_marketing=customer_info.get('opt_in_marketing', False)
            )
            logger.info('Created order successfully')
            
            # Mark shop order as paid
            shop_order.ordered = True
            shop_order.save()
            logger.info('shop_order is ordered')
            success_url = reverse('payments:payment-success') + \
                f'?order_id = {order.id}&payment_intent_id={payment_intent.id}'  
            logger.info('Want to save card info')      
            logger.info(f'{data}')
            logger.info(f'{payment_intent}')
            logger.info(f"Type: {type(data.get('save_payment_method'))}, Value: {data.get('save_payment_method')}")
            # Save payment method if requested
            if data.get('save_payment_method', False) is True and \
               hasattr(payment_intent, 'payment_method') and payment_intent.payment_method:
                logger.info(f'---initialising to save payment method for: {payment_intent.payment_method} ----')
                self.save_payment_method(request, payment_intent)
            
            # Clear session
            for key in ['payment_intent_id', 'payment_intent_client_secret', 
                       'payment_method', 'customer_info']:
                if key in request.session:
                    del request.session[key]
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirectUrl': success_url,
                })
            
            return redirect(success_url)
            
        except Exception as e:
            logger.error(f'---Failed loading payment success----')
            logger.error(f'Error handling payment success: {str(e)}', exc_info=True)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=400)
            
            messages.error(request, f"Error completing order: {str(e)}")
    
    def save_payment_method(self, request, payment_intent):
        try:
            if request.session.get('payment_method') == 'card' and \
               hasattr(payment_intent, 'payment_method') and payment_intent.payment_method:
                logger.info(f'---Loading payment intent keys -----')
                logger.info('===payment method keys and values=====')

                payment_method = stripe.PaymentMethod.retrieve(payment_intent.payment_method)

                logger.info(f'card_brand: {payment_method.card.brand}')
                logger.info(f'card_last4: {payment_method.card.last4}')
                logger.info(f'card_exp: {payment_method.card.exp_year}')

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
                
                logger.info(f'---Saved payment method sucessfully----')

        except Exception as e:
            logger.error(f"Error saving payment method: {str(e)}")

    def process_paypal_payment(self, request):
        try:
            # In a real implementation, this would:
            # 1. Create a PayPal order
            # 2. Store the PayPal order ID
            # 3. Redirect to PayPal approval URL
            
            # For demo purposes, simulate success
            return self.handle_payment_success(request, {'id': f'paypal_{datetime.now().timestamp()}'})
            
        except Exception as e:
            logger.error(f"Error processing PayPal payment: {str(e)}")
            messages.error(request, "Error processing PayPal payment")
            return redirect(reverse('payments:checkout') + '?step=2')
    
    def process_bank_transfer(self, request):
        try:
            # Generate bank transfer reference
            reference = f"BANK-{request.session['customer_info']['email']}-{int(datetime.now().timestamp())}"
            
            # In a real implementation, you would:
            # 1. Create an order record with "pending" status
            # 2. Send email with bank details
            # 3. Redirect to instructions page
            
            return redirect(reverse('payments:bank-transfer-instructions') + f'?reference={reference}')
            
        except Exception as e:
            logger.error(f"Error processing bank transfer: {str(e)}")
            messages.error(request, "Error processing bank transfer")
            return redirect(reverse('payments:checkout') + '?step=2')


class PaymentSuccessView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            logger.info(f'-----Loading payment sucess ----')
            order_id = request.GET.get('order_id')
            payment_intent_id = request.GET.get('payment_intent_id')

            if not (order_id or payment_intent_id):
                logger.error(f'---Missing order reference: {order_id}, {payment_intent_id}')
                raise Order.DoesNotExist('Missing order reference')

            order = self._get_order(request.user, order_id, payment_intent_id)

            context = {
                'order': order,
                'payment_intent_id': order.stripe_payment_intent_id
            }
            
            return render(request, 'payments/payments_success.html', context)
            
        except Order.DoesNotExist:
            logger.warning(f'Order not found for user : {request.user.id}')
            messages.error(request, "Order not found or access denied ")
            return redirect(reverse('shop:cart'))
        except Exception as e:
            logger.error(f"Error loading payment success: {str(e)}" , exc_info=True)
            messages.error(request, "Error loading order details for payment success")
            return redirect(reverse('shop:cart'))
    
    def _get_order(self, user, order_id=None, payment_intent_id=None):
        '''Secure order retrivial helper '''
        query = Q(user=user)  #user ownership

        if order_id:
            query &= Q(id=order_id)
        elif payment_intent_id:
            query &= Q(stripe_payment_intent_id=payment_intent_id)

        order = Order.objects.filter(query).first()
        if not order:
            logger.error('In payment success --- order does not exist ')
            raise Order.DoesNotExist
        return order


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f'Webhook invalid payload: {str(e)}')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f'Webhook signature verification failed: {str(e)}')
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f'Webhook processing error: {str(e)}')
        return HttpResponse(status=400)

    # Handle payment intent succeeded
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        try:
            order = Order.objects.filter(
                stripe_payment_intent_id=payment_intent.id
            ).first()
            
            if order and order.payment_status != 'completed':
                order.payment_status = 'completed'
                order.payment_details.update({
                    'webhook_received': True,
                    'amount_received': payment_intent.amount_received,
                    'payment_method': payment_intent.payment_method,
                    'charges': payment_intent.charges.data if hasattr(payment_intent, 'charges') else None
                })
                order.save()
                
                # Mark shop order as paid
                if order.shop_order:
                    order.shop_order.ordered = True
                    order.shop_order.save()
                
        except Exception as e:
            logger.error(f'Error processing payment_intent.succeeded: {str(e)}')
            
    # Handle payment intent failed
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        try:
            Order.objects.filter(
                stripe_payment_intent_id=payment_intent.id
            ).update(
                payment_status='failed',
                payment_details={
                    'last_payment_error': payment_intent.last_payment_error,
                    'failure_time': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f'Error processing payment_intent.payment_failed: {str(e)}')
    
    return HttpResponse(status=200)


@login_required
@require_POST
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
            'expiry': f"{method.card_exp_month}/{method.card_exp_year}",
            'is_default': method.is_default
        })
        
    except Exception as e:
        logger.error(f"Error saving card: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    

@login_required
def get_saved_cards(request):
    try:
        cards = SavedPaymentMethod.objects.filter(
            user=request.user, 
            payment_type='card'
        ).values('id', 'card_brand', 'card_last4', 'card_exp_month', 'card_exp_year')
        
        # Format expiry for display
        cards = [{
            **card,
            'expiry': f"{card['card_exp_month']}/{card['card_exp_year']}"
        } for card in cards]
        
        return JsonResponse(list(cards), safe=False)
    except Exception as e:
        logger.error(f"Error getting saved cards: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def use_saved_card(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('card_id')
        
        if not card_id:
            raise ValueError("Card ID is required")
        
        # Get the saved card
        card = SavedPaymentMethod.objects.get(
            id=card_id,
            user=request.user
        )
        
        shop_order = ShopOrder.objects.get(ordered=False, user=request.user)
        
        # Validate amount
        if not shop_order.total or shop_order.total <= 0:
            raise ValueError("Invalid order amount")
            
        amount = int(shop_order.total * 100)
        if amount < 50:  # Minimum charge amount
            raise ValueError("Amount too small")
        
        # Create payment intent with saved card
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer=request.user.stripe_customer_id if hasattr(request.user, 'stripe_customer_id') else None,
            payment_method=card.stripe_payment_method_id,
            confirm=True,
            off_session=True,  # Customer isn't present
            metadata={
                'user_id': request.user.id,
                'order_id': shop_order.id,
                'saved_card_id': card.id
            }
        )
        
        if intent.status == 'requires_action':
            return JsonResponse({
                'requires_action': True,
                'client_secret': intent.client_secret
            })
            
        if intent.status == 'succeeded':
            return JsonResponse({
                'status': 'succeeded',
                'session_id': intent.id
            })
            
        raise ValueError(f"Unexpected payment status: {intent.status}")
        
    except SavedPaymentMethod.DoesNotExist:
        return JsonResponse({'error': 'Card not found'}, status=404)
    except ShopOrder.DoesNotExist:
        return JsonResponse({'error': 'No active order found'}, status=400)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error using saved card: {str(e)}")
        return JsonResponse({'error': str(e.user_message)}, status=400)
    except Exception as e:
        logger.error(f"Error using saved card: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    


class PaymentsDashboard(TemplateView):
    template_name = 'payments/subscriptions.html'

