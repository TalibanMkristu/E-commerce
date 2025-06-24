export class DOMHelpers {
    static createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);
        
        // Set attributes
        for (const [key, value] of Object.entries(attributes)) {
            if (key === 'dataset') {
                for (const [dataKey, dataValue] of Object.entries(value)) {
                    element.dataset[dataKey] = dataValue;
                }
            } else if (key === 'style') {
                Object.assign(element.style, value);
            } else {
                element.setAttribute(key, value);
            }
        }
        
        // Append children
        if (Array.isArray(children)) {
            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else if (child instanceof Node) {
                    element.appendChild(child);
                }
            });
        } else if (typeof children === 'string') {
            element.textContent = children;
        } else if (children instanceof Node) {
            element.appendChild(children);
        }
        
        return element;
    }
    
    static delegate(event, selector, handler, context = document) {
        context.addEventListener(event, (e) => {
            let target = e.target;
            while (target && target !== context) {
                if (target.matches(selector)) {
                    handler.call(target, e);
                    break;
                }
                target = target.parentNode;
            }
        });
    }
    
    static toggleVisibility(element, show) {
        if (show) {
            element.style.display = '';
            element.setAttribute('aria-hidden', 'false');
        } else {
            element.style.display = 'none';
            element.setAttribute('aria-hidden', 'true');
        }
    }
    
    static scrollToElement(element, offset = 20) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}