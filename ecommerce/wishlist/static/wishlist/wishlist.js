// In your base template or static file
document.addEventListener('DOMContentLoaded', function() {
    // Set price alert
    document.querySelectorAll('.set-alert').forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const desiredPrice = prompt("Enter your desired price:");
            if (desiredPrice) {
                fetch(`/wishlist/set-alert/${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: new URLSearchParams({
                        'desired_price': desiredPrice
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) location.reload();
                });
            }
        });
    });
    
    // Add to wishlist AJAX
    document.querySelectorAll('.add-to-wishlist').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update wishlist counter in navbar
                    const counter = document.querySelector('.wishlist-counter');
                    if (counter) {
                        counter.textContent = parseInt(counter.textContent) + 1;
                    }
                    alert('Added to wishlist!');
                }
            });
        });
    });
});