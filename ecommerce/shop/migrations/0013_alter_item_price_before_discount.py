# Generated by Django 5.2.2 on 2025-06-12 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_orderitem_ordered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price_before_discount',
            field=models.FloatField(blank=True, max_length=10, null=True),
        ),
    ]
