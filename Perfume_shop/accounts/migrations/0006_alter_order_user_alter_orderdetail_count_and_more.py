# Generated by Django 5.0.4 on 2024-06-03 19:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_order_user_alter_orderdetail_count_and_more'),
        ('shop', '0004_alter_volumeperfumeprice_perfume_perfumevisit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='count',
            field=models.IntegerField(verbose_name='تعداد'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.order', verbose_name='سبد خرید'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='perfume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.perfume', verbose_name='محصول'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='volume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.volumeperfumeprice', verbose_name='حجم محصول'),
        ),
    ]
