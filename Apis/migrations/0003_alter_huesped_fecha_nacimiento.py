# Generated by Django 4.2.3 on 2023-07-24 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Apis', '0002_alter_user_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='huesped',
            name='fecha_nacimiento',
            field=models.DateField(),
        ),
    ]
