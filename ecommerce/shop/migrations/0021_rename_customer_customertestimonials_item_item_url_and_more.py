# Generated by Django 5.2.2 on 2025-06-23 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_alter_order_total_discount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Customer',
            new_name='CustomerTestimonials',
        ),
        migrations.AddField(
            model_name='item',
            name='item_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='stock',
            field=models.IntegerField(default=1),
        ),
    ]
