# Generated by Django 5.2.2 on 2025-06-11 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_contacts_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='address',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]
