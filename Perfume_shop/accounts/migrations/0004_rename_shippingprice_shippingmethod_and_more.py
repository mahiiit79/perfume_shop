# Generated by Django 5.0.4 on 2024-05-24 17:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_shippingprice'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShippingPrice',
            new_name='ShippingMethod',
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.shippingmethod', verbose_name='روش ارسال'),
        ),
    ]
