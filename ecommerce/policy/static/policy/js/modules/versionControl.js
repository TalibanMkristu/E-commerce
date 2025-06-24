export class VersionControl {
    constructor() {
        this.versionSelect = document.getElementById('version-select');
        this.versionHistoryToggle = document.getElementById('version-history-toggle');
        this.versionModal = document.getElementById('version-history-modal');
        this.init();
    }
    
    init() {
        if (this.versionSelect) {
            this.versionSelect.addEventListener('change', (e) => {
                this.handleVersionChange(e.target.value);
            });
        }
        
        if (this.versionHistoryToggle && this.versionModal) {
            this.setupVersionModal();
        }
    }
    
    handleVersionChange(version) {
        if (version === 'current') return;
        
        // In a real implementation, this would fetch the selected version
        console.log(`Loading version ${version}`);
        
        // Show warning if version is deprecated
        const selectedOption = this.versionSelect.querySelector(`option[value="${version}"]`);
        if (selectedOption && selectedOption.dataset.deprecated) {
            this.showDeprecationWarning(version);
        }
    }
    
    showDeprecationWarning(version) {
        // Would show a modal or toast notification
        console.warn(`Version ${version} is deprecated`);
    }
    
    setupVersionModal() {
        this.versionHistoryToggle.addEventListener('click', () => {
            this.openModal();
        });
        
        this.versionModal.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal();
        });
        
        // Close when clicking outside
        this.versionModal.addEventListener('click', (e) => {
            if (e.target === this.versionModal) {
                this.closeModal();
            }
        });
    }
    
    openModal() {
        this.versionModal.style.display = 'block';
        this.versionModal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
    
    closeModal() {
        this.versionModal.style.display = 'none';
        this.versionModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
}