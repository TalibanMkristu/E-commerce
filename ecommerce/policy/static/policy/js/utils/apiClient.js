export class APIClient {
    constructor(baseURL = '/api/') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }
    
    async request(endpoint, options = {}) {
        const url = this.baseURL + endpoint.replace(/^\//, '');
        const headers = { ...this.defaultHeaders, ...options.headers };
        
        if (options.body && typeof options.body !== 'string') {
            options.body = JSON.stringify(options.body);
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (!response.ok) {
                const error = new Error(response.statusText);
                error.response = response;
                throw error;
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    async get(endpoint, params = {}, options = {}) {
        const query = new URLSearchParams(params).toString();
        const url = query ? `${endpoint}?${query}` : endpoint;
        return this.request(url, { ...options, method: 'GET' });
    }
    
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: data
        });
    }
    
    setCSRFToken(token) {
        this.defaultHeaders['X-CSRFToken'] = token;
    }
    
    setAuthToken(token) {
        this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
}