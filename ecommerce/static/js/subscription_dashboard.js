// static/js/subscription_dashboard.js
function initSubscriptionDashboard() {
    return {
      showCancelModal: false,
      showUpgradeModal: false,
      showPaymentMethodModal: false,
      showSuccessNotification: false,
      showErrorNotification: false,
      successMessage: '',
      errorMessage: '',
      processingCancel: false,
      processingUpgrade: false,
      processingPayment: false,
      selectedPlan: null,
      stripe: null,
      cardElement: null,
      plans: JSON.parse(document.getElementById('plans-data').textContent),
      
      async toggleSubscriptionStatus() {
        this.processingCancel = true;
        try {
          const response = await fetch(this.$el.dataset.toggleUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': this.$el.dataset.csrfToken
            },
            body: JSON.stringify({
              action: this.$el.dataset.toggleAction
            })
          });
          
          const data = await response.json();
          if (response.ok) {
            this.successMessage = data.message || 'Subscription updated successfully';
            this.showSuccessNotification = true;
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          } else {
            throw new Error(data.error || 'Failed to update subscription');
          }
        } catch (error) {
          this.errorMessage = error.message;
          this.showErrorNotification = true;
        } finally {
          this.processingCancel = false;
          this.showCancelModal = false;
        }
      },
      
      async changePlan() {
        if (!this.selectedPlan) return;
        
        this.processingUpgrade = true;
        try {
          const response = await fetch(this.$el.dataset.changePlanUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': this.$el.dataset.csrfToken
            },
            body: JSON.stringify({
              plan_id: this.selectedPlan
            })
          });
          
          const data = await response.json();
          if (response.ok) {
            this.successMessage = data.message || 'Plan changed successfully';
            this.showSuccessNotification = true;
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          } else {
            throw new Error(data.error || 'Failed to change plan');
          }
        } catch (error) {
          this.errorMessage = error.message;
          this.showErrorNotification = true;
        } finally {
          this.processingUpgrade = false;
        }
      },
      
      initStripe() {
        if (!this.$el.dataset.stripeKey) return;
        
        const stripe = Stripe(this.$el.dataset.stripeKey);
        const elements = stripe.elements();
        const cardElement = elements.create('card');
        cardElement.mount('#card-element');
        
        this.stripe = stripe;
        this.cardElement = cardElement;
      },
      
      async updatePaymentMethod() {
        this.processingPayment = true;
        try {
          const { setupIntent, error } = await this.stripe.confirmCardSetup(
            this.$el.dataset.clientSecret, {
              payment_method: {
                card: this.cardElement,
                billing_details: {
                  name: this.$el.dataset.userName
                }
              }
            }
          );
          
          if (error) {
            throw new Error(error.message);
          }
          
          const response = await fetch(this.$el.dataset.paymentMethodUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': this.$el.dataset.csrfToken
            },
            body: JSON.stringify({
              payment_method: setupIntent.payment_method
            })
          });
          
          const data = await response.json();
          if (response.ok) {
            this.successMessage = data.message || 'Payment method updated successfully';
            this.showSuccessNotification = true;
            setTimeout(() => {
              window.location.reload();
            }, 2000);
          } else {
            throw new Error(data.error || 'Failed to update payment method');
          }
        } catch (error) {
          this.errorMessage = error.message;
          this.showErrorNotification = true;
        } finally {
          this.processingPayment = false;
        }
      },
      
      initChart() {
        const ctx = document.getElementById('usageChart');
        if (!ctx) return;
        
        const chartData = JSON.parse(document.getElementById('chart-data').textContent);
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: chartData.days,
            datasets: [{
              label: 'API Calls',
              data: chartData.data,
              backgroundColor: 'rgba(79, 70, 229, 0.05)',
              borderColor: 'rgba(79, 70, 229, 1)',
              borderWidth: 2,
              pointBackgroundColor: 'rgba(79, 70, 229, 1)',
              pointRadius: 3,
              pointHoverRadius: 5,
              tension: 0.1,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                mode: 'index',
                intersect: false,
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(0, 0, 0, 0.05)'
                }
              },
              x: {
                grid: {
                  display: false
                }
              }
            }
          }
        });
      },
      
      init() {
        this.initStripe();
        this.initChart();
      }
    }
  }
  
  // Initialize when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    const dashboardEl = document.getElementById('subscription-dashboard');
    if (dashboardEl) {
      Alpine.data('subscriptionDashboard', initSubscriptionDashboard);
      Alpine.start();
    }
  });