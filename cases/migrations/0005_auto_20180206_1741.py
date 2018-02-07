# Generated by Django 2.0.1 on 2018-02-06 17:41

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0004_auto_20180206_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='damaged_amount',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=Decimal('0.0'), default_currency='USD', max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='incident',
            name='stolen_amount',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default=Decimal('0.0'), default_currency='USD', max_digits=12, null=True),
        ),
    ]
