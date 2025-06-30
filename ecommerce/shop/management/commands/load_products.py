import csv
import os
import requests
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Item
import random

CATEGORY_MAPPING = {
    "Café": "VG",
    "Electronics": "EL",
    "Books": "BK",
    "Fashion": "FS",
    # Add more as needed
}

LABEL_CHOICES = ['P', 'S', 'D']
SIZE_CHOICES = ['S', 'M', 'L']

class Command(BaseCommand):
    help = "Import products from CSV into Item model with image download and more"

    def download_image(self, url, title):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = slugify(title) + ".jpg"
                return File(BytesIO(response.content), name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Image download failed for {url}: {e}"))
        return None

    def handle(self, *args, **kwargs):
        with open('products.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                title = row['name']
                slug = slugify(title)

                # Ensure unique slug
                original_slug = slug
                counter = 1
                while Item.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1

                price = float(row['price_usd'])
                stock = int(row.get('stock', 1))
                discount = random.choice([0, 5, 10, 15])
                price_before_discount = round(price / (1 - discount / 100), 2) if discount else price

                # Category mapping from CSV to model
                category_name = row.get('category', 'Café')
                category_value = CATEGORY_MAPPING.get(category_name, 'VG')

                label = random.choice(LABEL_CHOICES)
                size = random.choice(SIZE_CHOICES)
                rating = round(random.uniform(3.5, 5.0), 1)
                description = row.get('description', 'This is a test description.')

                # Image download
                item_image = self.download_image(row.get('image_url', ''), title)

                # Create item
                item = Item(
                    title=title,
                    price=price,
                    item_url=row.get('image_url', ''),
                    stock=stock,
                    percentage_discount=discount if discount else None,
                    price_before_discount=price_before_discount if discount else None,
                    category=category_value,
                    label=label,
                    slug=slug,
                    rating=rating,
                    description=description,
                    size=size
                )

                if item_image:
                    item.item_image = item_image

                item.save()

        self.stdout.write(self.style.SUCCESS('Products imported with images, categories, and extras.'))
