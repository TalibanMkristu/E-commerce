export class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('theme-toggle');
        this.currentTheme = localStorage.getItem('legal-theme') || 'default';
        this.init();
    }
    
    init() {
        this.applyTheme(this.currentTheme);
        
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // Watch for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (localStorage.getItem('legal-theme') === null) {
                this.applyTheme(e.matches ? 'dark' : 'default');
            }
        });
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'default' ? 'dark' : 'default';
        this.applyTheme(newTheme);
        localStorage.setItem('legal-theme', newTheme);
    }
    
    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-legal-theme', theme);
        
        // Update toggle button state
        if (this.themeToggle) {
            const isDark = theme === 'dark';
            this.themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            this.themeToggle.querySelector('.theme-icon-light').style.display = isDark ? 'none' : 'inline';
            this.themeToggle.querySelector('.theme-icon-dark').style.display = isDark ? 'inline' : 'none';
        }
    }
}