export class DocumentVerifier {
    constructor(options) {
        this.options = options;
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkAutoVerify();
    }
    
    bindEvents() {
        document.getElementById('verify-document')?.addEventListener('click', () => this.verify());
    }
    
    checkAutoVerify() {
        if (new URLSearchParams(window.location.search).has('verify')) {
            this.verify();
        }
    }
    
    async verify() {
        const resultElement = document.getElementById('verification-result');
        resultElement.innerHTML = '<p class="verifying">Verifying document...</p>';
        resultElement.setAttribute('aria-busy', 'true');
        
        try {
            const response = await fetch(this.options.verificationEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    document_id: this.options.documentId,
                    version: this.options.version,
                    hash: this.options.hash,
                }),
            });
            
            const data = await response.json();
            
            if (data.valid) {
                resultElement.innerHTML = `
                    <p class="valid">
                        <span class="icon">✓</span>
                        Document verified successfully. This is an authentic, unaltered version.
                    </p>
                    <p class="signature-details">
                        Signed by: ${data.signed_by}<br>
                        Timestamp: ${new Date(data.timestamp).toLocaleString()}<br>
                        Blockchain TX: <a href="${data.tx_url}" target="_blank">${data.tx_id.substring(0, 12)}...</a>
                    </p>
                `;
            } else {
                resultElement.innerHTML = `
                    <p class="invalid">
                        <span class="icon">⚠️</span>
                        Verification failed: ${data.reason || 'Document integrity compromised'}
                    </p>
                `;
            }
        } catch (error) {
            resultElement.innerHTML = `
                <p class="error">
                    <span class="icon">⚠️</span>
                    Verification error: ${error.message}
                </p>
            `;
        } finally {
            resultElement.setAttribute('aria-busy', 'false');
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}