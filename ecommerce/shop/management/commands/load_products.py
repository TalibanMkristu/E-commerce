import csv
import os
import requests
import random
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Item

CATEGORY_MAPPING = {
    "VG": "VG",
    "EL": "EL",
    "BK": "BK",
    "FS": "FS",
    # Extend as needed
}

LABEL_CHOICES = ['P', 'S', 'D']
SIZE_CHOICES = ['S', 'M', 'L', 'XL']

class Command(BaseCommand):
    help = "Import products from CSV into Item model with optional image download"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file (absolute or relative)")

    def download_image(self, url, title):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filename = slugify(title) + ".jpg"
                return File(BytesIO(response.content), name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Image download failed for {url}: {e}"))
        return None

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                title = row.get('title', 'Untitled')
                slug = slugify(title)

                # Ensure unique slug
                original_slug = slug
                counter = 1
                while Item.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1

                try:
                    price = float(row['price'])
                except (ValueError, KeyError):
                    price = 0.0

                stock = int(row.get('stock', 1))
                discount = float(row.get('percentage_discount', 0)) or 0
                price_before = float(row.get('price_before_discount') or (price / (1 - discount/100) if discount else price))

                category = row.get('category', 'VG')
                category_value = CATEGORY_MAPPING.get(category, 'VG')

                label = row.get('label', random.choice(LABEL_CHOICES))
                size = row.get('size', random.choice(SIZE_CHOICES))
                rating = float(row.get('rating', round(random.uniform(3.5, 5.0), 1)))
                description = row.get('description', 'This is a test description.')

                image_url = row.get('item_url', '')
                image_file = self.download_image(image_url, title)

                item = Item(
                    title=title,
                    price=price,
                    item_url=image_url,
                    stock=stock,
                    percentage_discount=discount,
                    price_before_discount=price_before,
                    category=category_value,
                    label=label,
                    slug=slug,
                    rating=rating,
                    description=description,
                    size=size,
                )

                if image_file:
                    item.item_image = image_file

                item.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Imported {count} products from {csv_path}'))
