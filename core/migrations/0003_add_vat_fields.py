from django.db import migrations, models
from decimal import Decimal

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cartitem_variant_details_orderitem_variant_details_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='net_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='vat_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='net_unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='vat_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='net_subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='vat_subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]