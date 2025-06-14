document.addEventListener('DOMContentLoaded', function() {
    // Theme Management
    const themeToggle = document.createElement('div');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = `
        <button id="themeToggleBtn" aria-label="Toggle dark mode">
            <i class="fas fa-moon"></i>
            <i class="fas fa-sun"></i>
        </button>
    `;
    document.body.appendChild(themeToggle);

    // Initialize loading state with fallback
    const loadingOverlay = document.getElementById('loadingOverlay');
    function hideLoadingOverlay() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
            // Ensure loading overlay is hidden even if CSS fails
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 1000);
        }
    }

    // Set timeout to ensure loading overlay disappears
    if (loadingOverlay) {
        loadingOverlay.classList.add('active');
        // Fallback in case the timeout fails
        const loadingTimeout = setTimeout(hideLoadingOverlay, 1500);
        
        // Also hide when everything is loaded
        window.addEventListener('load', () => {
            clearTimeout(loadingTimeout);
            hideLoadingOverlay();
        });
    }

    // Initialize Particle Canvas with enhanced animations
    const initParticleCanvas = () => {
        const canvas = document.getElementById('particleCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Theme state
        let darkMode = true; // Default to dark theme
        const toggleBtn = document.getElementById('themeToggleBtn');

        // Set initial theme
        function initTheme() {
            const savedMode = localStorage.getItem('darkMode');
            darkMode = savedMode ? savedMode === 'true' : true;
            applyTheme(darkMode);
            updateThemeButton();
        }

        function applyTheme(isDark) {
            document.body.classList.toggle('dark-theme', isDark);
            const bgGradient = document.querySelector('.bg-gradient');
            const bgPattern = document.querySelector('.bg-pattern');
            
            if (bgGradient && bgPattern) {
                if (isDark) {
                    bgGradient.style.background = '#000000';
                    bgPattern.style.opacity = '0.15';
                } else {
                    bgGradient.style.background = 'linear-gradient(135deg, #1a1a1a 0%, #000000 100%)';
                    bgPattern.style.opacity = '0.3';
                }
            }
        }

        function updateThemeButton() {
            if (toggleBtn) {
                const moonIcon = toggleBtn.querySelector('.fa-moon');
                const sunIcon = toggleBtn.querySelector('.fa-sun');
                if (moonIcon && sunIcon) {
                    moonIcon.style.display = darkMode ? 'none' : 'inline-block';
                    sunIcon.style.display = darkMode ? 'inline-block' : 'none';
                }
            }
        }

        function saveThemePreference() {
            localStorage.setItem('darkMode', darkMode);
        }

        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                darkMode = !darkMode;
                applyTheme(darkMode);
                updateThemeButton();
                saveThemePreference();
            });
        }

        initTheme();

        // Enhanced particle system with connections
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
                this.lightness = darkMode ? Math.random() * 0.5 + 0.5 : Math.random() * 0.3 + 0.2;
                this.color = `hsla(46, 65%, ${this.lightness * 100}%, ${Math.random() * 0.3 + 0.1})`;
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
        let animationId;
        let lastTime = 0;
        const animate = (currentTime) => {
            if (!lastTime) lastTime = currentTime;
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;

            // Clear with semi-transparent for trail effect
            ctx.fillStyle = darkMode ? 'rgba(0, 0, 0, 0.1)' : 'rgba(250, 250, 250, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Update and draw particles
            particles.forEach(particle => {
                particle.updatePosition();
                particle.draw();
            });

            // Connect nearby particles
            connectParticles(particles);
            
            animationId = requestAnimationFrame(animate);
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

        // Clean up animation when leaving page
        window.addEventListener('beforeunload', () => {
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
        });
    };

    // Initialize social login buttons with enhanced animations
    const initSocialLogins = () => {
        const socialButtons = document.querySelectorAll('.btn-social');
        
        socialButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const service = this.classList[2]?.split('-')[1];
                if (!service) return;
                
                this.classList.add('loading');
                
                setTimeout(() => {
                    this.classList.remove('loading');
                    console.log(`Authenticating with ${service}...`);
                }, 1500);
            });
            
            // Add tooltip effect
            button.addEventListener('mouseenter', function() {
                const service = this.classList[2]?.split('-')[1];
                if (!service) return;
                
                const tooltip = document.createElement('div');
                tooltip.className = 'social-tooltip';
                tooltip.textContent = `Continue with ${service.charAt(0).toUpperCase() + service.slice(1)}`;
                this.appendChild(tooltip);
                
                setTimeout(() => {
                    tooltip.classList.add('visible');
                }, 10);
                
                // Enhanced hover effects
                this.style.transform = 'translateY(-5px) scale(1.1)';
                this.style.boxShadow = document.body.classList.contains('dark-theme') 
                    ? '0 8px 20px rgba(212, 175, 55, 0.3)' 
                    : '0 8px 20px rgba(0, 0, 0, 0.4)';
            });
            
            button.addEventListener('mouseleave', function() {
                const tooltip = this.querySelector('.social-tooltip');
                if (tooltip) {
                    tooltip.classList.remove('visible');
                    setTimeout(() => {
                        tooltip.remove();
                    }, 300);
                }
                
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
            });
        });
    };

    // Form validation and submission with animations
    const initForms = () => {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registrationForm');
        const loadingOverlay = document.getElementById('loadingOverlay');
        
        const handleFormSubmit = (form, submitBtnId) => {
            if (!form) return;
            
            form.addEventListener('submit', function(e) {
                const submitBtn = document.getElementById(submitBtnId);
                if (!submitBtn) return;
                
                submitBtn.classList.add('loading');
                if (loadingOverlay) loadingOverlay.classList.add('active');
                
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
                    if (loadingOverlay) loadingOverlay.classList.remove('active');
                    
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