from django.urls import path
from . import views

app_name = 'policy'

urlpatterns = [
    path('legal-documentation/', views.LegalDocumentView.as_view(), name="legal"),
    path('terms-of-services/', views.TermsOfServiceView.as_view(), name="terms"),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name="privacy"), 
    path('document-verification/', views.DocumentVerificationView.as_view(), name="document-verification")

]