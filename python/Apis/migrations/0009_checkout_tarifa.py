# Generated by Django 4.2.3 on 2023-07-27 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Apis', '0008_alter_reserva_peticiones'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='tarifa',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=7),
            preserve_default=False,
        ),
    ]