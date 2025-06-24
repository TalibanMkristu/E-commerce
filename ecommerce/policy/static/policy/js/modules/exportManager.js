export class ExportManager {
    constructor() {
        this.exportButtons = document.querySelectorAll('[data-export]');
        this.init();
    }
    
    init() {
        this.exportButtons.forEach(button => {
            button.addEventListener('click', () => {
                const format = button.dataset.export;
                this.handleExport(format);
            });
        });
    }
    
    async handleExport(format) {
        try {
            const documentId = document.body.dataset.documentId;
            const version = document.body.dataset.documentVersion;
            
            switch (format) {
                case 'pdf':
                    await this.exportAsPDF(documentId, version);
                    break;
                case 'markdown':
                    await this.exportAsMarkdown(documentId, version);
                    break;
                case 'html':
                    await this.exportAsHTML(documentId, version);
                    break;
                case 'json':
                    await this.exportAsJSON(documentId, version);
                    break;
                default:
                    console.error('Unsupported export format:', format);
            }
        } catch (error) {
            console.error('Export failed:', error);
            this.showExportError(error);
        }
    }
    
    async exportAsPDF(documentId, version) {
        // Use pdfmake or call server-side PDF generation
        console.log(`Exporting ${documentId} v${version} as PDF`);
        
        // Example using pdfmake
        if (window.pdfMake) {
            const docDefinition = this.generatePDFDefinition();
            pdfMake.createPdf(docDefinition).download(`${documentId}_v${version}.pdf`);
        } else {
            window.location.href = `/legal/export/pdf/?doc=${documentId}&version=${version}`;
        }
    }
    
    generatePDFDefinition() {
        // Extract content from the page and format for PDF
        const title = document.querySelector('.document-title').textContent;
        const effectiveDate = document.querySelector('.effective-date').textContent;
        const content = Array.from(document.querySelectorAll('.section'))
            .map(section => ({
                text: section.querySelector('.section-title').textContent,
                style: 'header'
            }));
        
        return {
            content: [
                { text: title, style: 'title' },
                { text: effectiveDate, style: 'subheader' },
                ...content
            ],
            styles: {
                title: { fontSize: 18, bold: true, margin: [0, 0, 0, 10] },
                subheader: { fontSize: 14, bold: true, margin: [0, 10, 0, 5] },
                header: { fontSize: 12, bold: true, margin: [0, 5, 0, 5] }
            }
        };
    }
    
    async exportAsMarkdown(documentId, version) {
        console.log(`Exporting ${documentId} v${version} as Markdown`);
        // Implementation would convert HTML to Markdown
        window.location.href = `/legal/export/markdown/?doc=${documentId}&version=${version}`;
    }
    
    async exportAsHTML(documentId, version) {
        console.log(`Exporting ${documentId} v${version} as HTML`);
        // Implementation would sanitize and package the HTML
        window.location.href = `/legal/export/html/?doc=${documentId}&version=${version}`;
    }
    
    async exportAsJSON(documentId, version) {
        console.log(`Exporting ${documentId} v${version} as JSON`);
        // Implementation would structure the document as JSON-LD
        window.location.href = `/legal/export/json/?doc=${documentId}&version=${version}`;
    }
    
    showExportError(error) {
        const errorElement = document.createElement('div');
        errorElement.className = 'export-error';
        errorElement.innerHTML = `
            <p>Export failed: ${error.message}</p>
            <button class="btn-text">Try again</button>
        `;
        
        document.body.appendChild(errorElement);
        setTimeout(() => errorElement.remove(), 5000);
    }
}