document.addEventListener('DOMContentLoaded', () => {
    const stripe = Stripe('{{ STRIPE_PUBLIC_KEY }}');
    const elements = stripe.elements();
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
    
    const form = document.getElementById('payment-form');
    const submitBtn = document.getElementById('submit');
    const spinner = document.getElementById('spinner');
    const buttonText = document.getElementById('button-text');
    const paymentMessage = document.getElementById('payment-message');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        submitBtn.disabled = true;
        buttonText.classList.add('hidden');
        spinner.classList.remove('hidden');
        
        // Confirm payment
        const { error } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: window.location.origin + '{% url "payment-success" %}',
            }
        });
        
        if (error) {
            paymentMessage.textContent = error.message;
            paymentMessage.classList.remove('hidden');
            
            // Reset button
            submitBtn.disabled = false;
            buttonText.classList.remove('hidden');
            spinner.classList.add('hidden');
            
            // Shake animation for error
            gsap.to(paymentMessage, { 
                x: [-5, 5, -5, 5, 0], 
                duration: 0.5,
                ease: "power1.out" 
            });
        }
    });
});