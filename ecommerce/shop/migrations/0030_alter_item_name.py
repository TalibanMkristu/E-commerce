# Generated by Django 5.2.3 on 2025-06-30 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0029_item_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
