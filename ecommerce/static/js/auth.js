document.addEventListener('DOMContentLoaded', function() {
    // Initialize loading state
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    // Show loading overlay initially for 1.5s to prevent FOUC
    loadingOverlay.classList.add('active');
    setTimeout(() => {
        loadingOverlay.classList.remove('active');
    }, 1500);

    // Particle canvas animation
    const initParticleCanvas = () => {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const ctx = canvas.getContext('2d');
        const particles = [];
        const particleCount = window.innerWidth < 768 ? 30 : 50;
        const goldenRatio = (1 + Math.sqrt(5)) / 2;
        const angleIncrement = Math.PI * 2 * goldenRatio;

        class Particle {
            constructor(index) {
                this.size = Math.random() * 3 + 1;
                this.angle = index * angleIncrement;
                this.distance = Math.random() * 200 + 100;
                this.speed = Math.random() * 0.002 + 0.001;
                this.color = `hsla(46, 65%, ${Math.random() * 30 + 60}%, ${Math.random() * 0.3 + 0.1})`;
                this.centerX = canvas.width / 2;
                this.centerY = canvas.height / 2;
                this.updatePosition();
            }

            updatePosition() {
                this.angle += this.speed;
                this.x = this.centerX + Math.cos(this.angle) * this.distance;
                this.y = this.centerY + Math.sin(this.angle) * this.distance;
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Initialize particles in spiral pattern
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle(i));
        }

        // Animation loop with optimized rendering
        let lastTime = 0;
        const animate = (currentTime) => {
            if (!lastTime) lastTime = currentTime;
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            // Clear with semi-transparent for trail effect
            ctx.fillStyle = 'rgba(10, 10, 10, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update and draw particles
            particles.forEach(particle => {
                particle.updatePosition();
                particle.draw();
            });

            // Connect nearby particles
            connectParticles(particles);
            
            requestAnimationFrame(animate);
        };

        // Connect particles with elegant lines
        const connectParticles = (particles) => {
            ctx.lineWidth = 0.5;
            
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < 120) {
                        const opacity = 1 - distance / 120;
                        ctx.strokeStyle = `hsla(46, 65%, 70%, ${opacity * 0.3})`;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
        };

        // Handle window resize with debounce
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                particles.forEach((particle, index) => {
                    particle.centerX = canvas.width / 2;
                    particle.centerY = canvas.height / 2;
                    particle.distance = Math.random() * 200 + 100;
                });
            }, 200);
        });

        // Start animation
        animate(0);
    };

    // Initialize social login buttons
    const initSocialLogins = () => {
        const socialButtons = document.querySelectorAll('.btn-social');
        
        socialButtons.forEach(button => {
            button.addEventListener('click', function() {
                const service = this.classList[2].split('-')[1]; // Get service name
                loadingOverlay.classList.add('active');
                
                // Simulate API call with timeout
                setTimeout(() => {
                    loadingOverlay.classList.remove('active');
                    // In production, replace with actual OAuth flow
                    console.log(`Initiated ${service} login`);
                }, 1500);
            });
            
            // Add tooltip effect
            button.addEventListener('mouseenter', function() {
                const service = this.classList[2].split('-')[1];
                const tooltip = document.createElement('div');
                tooltip.className = 'social-tooltip';
                tooltip.textContent = `Continue with ${service.charAt(0).toUpperCase() + service.slice(1)}`;
                this.appendChild(tooltip);
                
                setTimeout(() => {
                    tooltip.classList.add('visible');
                }, 10);
            });
            
            button.addEventListener('mouseleave', function() {
                const tooltip = this.querySelector('.social-tooltip');
                if (tooltip) {
                    tooltip.classList.remove('visible');
                    setTimeout(() => {
                        tooltip.remove();
                    }, 300);
                }
            });
        });
    };

    // Form validation and submission
    const initForms = () => {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registrationForm');
        
        const handleFormSubmit = (form, submitBtnId) => {
            if (!form) return;
            
            form.addEventListener('submit', function(e) {
                const submitBtn = document.getElementById(submitBtnId);
                submitBtn.classList.add('loading');
                loadingOverlay.classList.add('active');
                
                // Validate required fields
                let isValid = true;
                const requiredFields = form.querySelectorAll('[required]');
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        field.classList.add('is-invalid');
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    submitBtn.classList.remove('loading');
                    loadingOverlay.classList.remove('active');
                    
                    // Scroll to first invalid field
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }
                }
            });
        };
        
        handleFormSubmit(loginForm, 'loginBtn');
        handleFormSubmit(registerForm, 'registerBtn');
    };

    // Initialize all components
    initParticleCanvas();
    initSocialLogins();
    initForms();
});




// Add click handlers for social buttons
document.querySelectorAll('.btn-social').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Add loading state
        this.classList.add('loading');
        
        // Determine platform
        const platform = this.classList[2].split('-')[1]; // Gets 'apple', 'google', etc.
        
        // Simulate API call (replace with actual OAuth implementation)
        setTimeout(() => {
            this.classList.remove('loading');
            console.log(`Authenticating with ${platform}...`);
            // window.location.href = `/auth/${platform}`;
        }, 1500);
    });
    
    // Enhanced hover effects
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-3px) scale(1.1)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = '';
    });
});