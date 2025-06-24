// IntersectionObserver polyfill for older browsers
if (!('IntersectionObserver' in window)) {
    import('intersection-observer').then(() => {
        console.log('IntersectionObserver polyfill loaded');
    });
}

// Custom event polyfill
if (typeof window.CustomEvent !== 'function') {
    function CustomEvent(event, params) {
        params = params || { bubbles: false, cancelable: false, detail: null };
        const evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(event, params.bubbles, params.cancelable, params.detail);
        return evt;
    }
    window.CustomEvent = CustomEvent;
}