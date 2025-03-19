# Generated by Django 5.1.7 on 2025-03-13 09:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_alter_order_options_alter_orderitem_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingaddress',
            options={'ordering': ['-id'], 'verbose_name': 'Shipping Address', 'verbose_name_plural': 'Shipping Addresses'},
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='payment.order'),
        ),
    ]
