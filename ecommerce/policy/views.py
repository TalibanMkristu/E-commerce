from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.signing import TimestampSigner, BadSignature
from datetime import datetime, date
import hashlib
import json

class LegalDocumentView(TemplateView):
    """Base view for all legal documents with advanced features"""
    template_name = 'policy/base.html'
    document_type = None
    current_version = '2.3.1'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'company_name': 'Your Company',
            'company_domain': 'yourdomain.com',
            'company_address': '123 Legal Street\nCompliance City',
            'legal_entity_number': 'LEI-12345678',
            'current_version': self.current_version,
            'effective_date': self.get_effective_date(),
            'last_updated': self.get_last_updated(),
            'document_id': self.get_document_id(),
            'content_hash': self.get_content_hash(),
            'previous_versions': self.get_previous_versions(),
            'geolocation_enabled': True,
            'show_version_warning': self.request.GET.get('version') != self.current_version,
        })
        return context
    
    def get_effective_date(self):
        # Would normally come from database
        return date(2023, 1, 1)
    
    def get_last_updated(self):
        # Would normally come from database
        return date.today()
    
    def get_document_id(self):
        return f"{self.document_type}-{self.current_version}-{self.get_last_updated():%Y%m%d}"
    
    def get_content_hash(self):
        content = self.get_document_content()
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_document_content(self):
        """Should be overridden by child classes to return the actual document content"""
        return ""
    
    def get_previous_versions(self):
        # Would normally come from version control system
        return [
            {'number': '2.2.0', 'date': date(2022, 7, 15), 'deprecated': True},
            {'number': '2.1.3', 'date': date(2022, 3, 10), 'deprecated': True},
        ]

class TermsOfServiceView(LegalDocumentView):
    """Advanced Terms of Service view"""
    document_type = 'TOS'
    template_name = 'policy/terms.html'
    
    def get_document_content(self):
        # This would generate the actual content for hashing
        return json.dumps({
            'title': 'Terms of Service',
            'sections': self.get_sections(),
            'effective_date': self.get_effective_date().isoformat(),
        })
    
    def get_sections(self):
        # Would come from database or structured files
        return [...]

class PrivacyPolicyView(LegalDocumentView):
    """Advanced Privacy Policy view"""
    document_type = 'PP'
    template_name = 'policy/privacy.html'
    
    def get_document_content(self):
        return json.dumps({
            'title': 'Privacy Policy',
            'sections': self.get_sections(),
            'effective_date': self.get_effective_date().isoformat(),
        })

class DocumentVerificationView(LoginRequiredMixin, View):
    """API endpoint for document verification"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            signer = TimestampSigner()
            
            # Verify the document hash
            expected_hash = self.calculate_expected_hash(data['document_id'], data['version'])
            if data['hash'] != expected_hash:
                return JsonResponse({'valid': False, 'reason': 'Hash mismatch'}, status=400)
            
            # Verify the signature (in a real implementation)
            # signer.unsign(f"{data['document_id']}:{data['version']}:{data['hash']}")
            
            return JsonResponse({
                'valid': True,
                'signed_by': 'Legal Department',
                'timestamp': datetime.now().isoformat(),
                'tx_id': '0x123...abc',  # Mock blockchain transaction
                'tx_url': 'https://etherscan.io/tx/0x123...abc',
            })
            
        except BadSignature:
            return JsonResponse({'valid': False, 'reason': 'Invalid signature'}, status=400)
        except Exception as e:
            return JsonResponse({'valid': False, 'reason': str(e)}, status=500)
    
    def calculate_expected_hash(self, doc_id, version):
        # In reality, would fetch the document and compute hash
        mock_content = f"{doc_id}-{version}-content"
        return hashlib.sha256(mock_content.encode('utf-8')).hexdigest()