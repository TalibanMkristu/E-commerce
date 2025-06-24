document.addEventListener('DOMContentLoaded', function() {
    // Check if Alpine is loaded
    if (typeof Alpine === 'undefined') {
        console.error('Alpine.js is not loaded');
        return;
    }

    Alpine.data('checkout', function() {
        return {
            currentStep: 1,
            checkoutSteps: ['Information', 'Payment', 'Review'],
            selectedPaymentMethod: 'card',
            savePaymentMethod: false,
            agreedToTerms: false,
            processingPayment: false,
            stripe: null,
            elements: null,
            cardElement: null,
            paymentIntentClientSecret: null,

            async init() {
                // Load Stripe.js
                if (!window.Stripe) {
                    await this.loadScript('https://js.stripe.com/v3/');
                }
                
                this.stripe = Stripe('{{ STRIPE_PUBLISHABLE_KEY }}');
                this.setupElements();
                this.setupEventListeners();
            },

            setupElements() {
                const appearance = {
                    theme: document.documentElement.classList.contains('dark') ? 'night' : 'stripe',
                    variables: {
                        colorPrimary: '#6366f1',
                        colorBackground: getComputedStyle(document.documentElement).getPropertyValue('--bg-color') || '#ffffff',
                        colorText: getComputedStyle(document.documentElement).getPropertyValue('--text-color') || '#1a1a1a',
                        colorDanger: '#ef4444',
                        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                        spacingUnit: '4px',
                        borderRadius: '6px'
                    }
                };
                
                this.elements = this.stripe.elements({ appearance });
                
                if (this.selectedPaymentMethod === 'card') {
                    this.setupCardElement();
                }
            },

            setupCardElement() {
                if (this.cardElement) {
                    this.cardElement.unmount();
                }
                
                this.cardElement = this.elements.create('card', {
                    style: {
                        base: {
                            iconColor: '#6366f1',
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color') || '#1a1a1a',
                            fontWeight: '500',
                            fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                            fontSize: '16px',
                            fontSmoothing: 'antialiased',
                            '::placeholder': {
                                color: '#6b7280'
                            }
                        },
                        invalid: {
                            color: '#ef4444'
                        }
                    }
                });
                
                this.cardElement.mount('#card-element');
                
                this.cardElement.on('change', (event) => {
                    const displayError = document.getElementById('card-errors');
                    if (event.error) {
                        displayError.textContent = event.error.message;
                        displayError.classList.remove('hidden');
                    } else {
                        displayError.textContent = '';
                        displayError.classList.add('hidden');
                    }
                });
            },

            setupEventListeners() {
                // Watch for payment method changes
                this.$watch('selectedPaymentMethod', (value) => {
                    if (value === 'card' && !this.cardElement) {
                        this.setupCardElement();
                    }
                });
                
                // Watch for dark mode changes
                const observer = new MutationObserver(() => {
                    if (this.elements) {
                        this.elements.update({
                            appearance: {
                                theme: document.documentElement.classList.contains('dark') ? 'night' : 'stripe'
                            }
                        });
                    }
                });
                
                observer.observe(document.documentElement, {
                    attributes: true,
                    attributeFilter: ['class']
                });
            },

            async loadScript(url) {
                return new Promise((resolve, reject) => {
                    const script = document.createElement('script');
                    script.src = url;
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                });
            },

            async validateStep1() {
                if (!this.customer.firstName || !this.customer.lastName || !this.customer.email) {
                    this.showToast('Please fill all required fields', 'error');
                    return false;
                }
                
                if (!/^\S+@\S+\.\S+$/.test(this.customer.email)) {
                    this.showToast('Please enter a valid email address', 'error');
                    return false;
                }
                
                return true;
            },

            async processStep1() {
                if (!await this.validateStep1()) {
                    return;
                }
                
                if (this.selectedPaymentMethod === 'card') {
                    try {
                        await this.createPaymentIntent();
                    } catch (error) {
                        this.showToast('Failed to initialize payment: ' + error.message, 'error');
                        return;
                    }
                }
                
                this.currentStep = 2;
                this.scrollToTop();
            },

            async createPaymentIntent() {
                try {
                    const response = await fetch('{% url "payments:checkout" %}', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        body: JSON.stringify({
                            action: 'create_payment_intent'
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        throw new Error(result.error);
                    }
                    
                    this.paymentIntentClientSecret = result.clientSecret;
                    return result;
                } catch (error) {
                    console.error('Payment intent creation failed:', error);
                    throw error;
                }
            },

            async processCardPayment() {
                if (!this.paymentIntentClientSecret) {
                    await this.createPaymentIntent();
                }
                
                this.processingPayment = true;
                
                try {
                    const { error, paymentIntent } = await this.stripe.confirmCardPayment(
                        this.paymentIntentClientSecret, {
                            payment_method: {
                                card: this.cardElement,
                                billing_details: {
                                    name: `${this.customer.firstName} ${this.customer.lastName}`,
                                    email: this.customer.email
                                }
                            },
                            save_payment_method: this.savePaymentMethod
                        }
                    );
                    
                    if (error) {
                        if (error.code === 'card_declined') {
                            this.showToast('Your card was declined. Please try another payment method.', 'error');
                        } else {
                            this.showToast(error.message, 'error');
                        }
                        throw error;
                    }
                    
                    // Verify payment with backend
                    const response = await fetch('{% url "payments:checkout" %}', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        body: JSON.stringify({
                            action: 'confirm_payment',
                            paymentIntentId: paymentIntent.id,
                            save_payment_method: this.savePaymentMethod
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        throw new Error(result.error);
                    }
                    
                    if (result.requiresAction) {
                        const { error: confirmError } = await this.stripe.confirmCardPayment(
                            result.clientSecret
                        );
                        
                        if (confirmError) {
                            throw confirmError;
                        }
                        
                        return this.processCardPayment();
                    }
                    
                    window.location.href = result.redirectUrl;
                    
                } catch (error) {
                    console.error('Payment error:', error);
                    this.showToast('Payment failed: ' + (error.message || 'Unknown error'), 'error');
                    this.processingPayment = false;
                }
            },

            showToast(message, type = 'success') {
                // Implement your toast notification system
                console.log(`${type}: ${message}`);
                // Example: this.$dispatch('notify', {type, message});
            },

            scrollToTop() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        };
    });
});