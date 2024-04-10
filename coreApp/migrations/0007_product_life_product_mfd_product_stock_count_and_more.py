# Generated by Django 4.2.7 on 2024-01-28 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreApp', '0006_alter_productimages_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='life',
            field=models.CharField(blank=True, default='100 days', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='mfd',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_count',
            field=models.CharField(blank=True, default='8', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='type',
            field=models.CharField(blank=True, default='Catalyst', max_length=100, null=True),
        ),
    ]
