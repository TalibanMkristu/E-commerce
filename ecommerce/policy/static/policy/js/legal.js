import { DocumentNavigation } from './modules/documentNavigation.js';
import { ThemeManager } from './modules/themeManager.js';
import { VersionControl } from './modules/versionControl.js';
import { DocumentVerifier } from './modules/documentVerifier.js';
import { ExportManager } from './modules/exportManager.js';
import { Analytics } from './modules/analytics.js';
import { polyfills } from './utils/polyfills.js';

class LegalApplication {
    constructor() {
        // Load polyfills first
        polyfills();
        
        // Initialize modules
        this.modules = {
            navigation: new DocumentNavigation(),
            theme: new ThemeManager(),
            versionControl: new VersionControl(),
            exports: new ExportManager(),
            verifier: document.getElementById('verify-document') ? 
                new DocumentVerifier({
                    documentId: document.body.dataset.documentId,
                    version: document.body.dataset.documentVersion,
                    hash: document.querySelector('.doc-hash')?.textContent,
                    verificationEndpoint: '/legal/verify/'
                }) : null,
            analytics: new Analytics({
                trackingId: 'UA-XXXXX-Y',
                anonymizeIp: true,
                respectDoNotTrack: true
            })
        };
        
        // Setup print functionality
        this.setupPrintButton();
    }
    
    setupPrintButton() {
        document.querySelector('.btn-print')?.addEventListener('click', () => {
            window.print();
        });
    }
}

// Initialize when DOM is loaded
if (document.readyState !== 'loading') {
    new LegalApplication();
} else {
    document.addEventListener('DOMContentLoaded', () => new LegalApplication());
}