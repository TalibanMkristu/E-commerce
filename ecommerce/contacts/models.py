from django.db import models

# Create your models here.
class Contacts(models.Model):
    address = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.website
    
    def claen_website(self):
        website = self.website
        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"
        return website
    
    def formatedPhone(self):
        phone = self.phone.replace(' ', '').replace('-', '')
        return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
    
    def formatedAddress(self):
        return self.address.replace(',', '<br>')
