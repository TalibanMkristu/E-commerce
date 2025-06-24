export class DocumentNavigation {
    constructor() {
        this.nav = document.querySelector('.legal-nav');
        this.sections = document.querySelectorAll('section[id], div[id]');
        this.init();
    }
    
    init() {
        if (!this.nav) return;
        
        this.setupSmoothScrolling();
        this.setupSectionObserver();
        this.setupMobileMenu();
    }
    
    setupSmoothScrolling() {
        this.nav.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (!link) return;
            
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const target = document.querySelector(targetId);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL without jumping
                history.pushState(null, null, targetId);
                
                // Update active state
                this.setActiveLink(link);
            }
        });
    }
    
    setupSectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');
                    if (id) {
                        const link = this.nav.querySelector(`a[href="#${id}"]`);
                        if (link) this.setActiveLink(link);
                    }
                }
            });
        }, options);
        
        this.sections.forEach(section => {
            observer.observe(section);
        });
    }
    
    setActiveLink(activeLink) {
        this.nav.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            link.setAttribute('aria-current', null);
        });
        
        activeLink.classList.add('active');
        activeLink.setAttribute('aria-current', 'page');
    }
    
    setupMobileMenu() {
        const toggle = this.nav.querySelector('.nav-more-toggle');
        if (!toggle) return;
        
        toggle.addEventListener('click', () => {
            const expanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !expanded);
        });
        
        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.nav.contains(e.target)) {
                toggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
}