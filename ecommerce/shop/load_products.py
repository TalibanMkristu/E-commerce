# management/commands/import_products.py
import csv
from django.core.management.base import BaseCommand
from .models import Item  

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open('products.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Item.objects.update_or_create(
                    id=row['id'],
                    title=row['name'],
                    defaults={
                        'description': row['description'],
                        'category': row['category'],
                        'price': row['price_usd'],
                        'stock': row['stock'],
                        'image_url': row['image_url']
                    }
                )
        self.stdout.write(self.style.SUCCESS('Products imported successfully.'))
