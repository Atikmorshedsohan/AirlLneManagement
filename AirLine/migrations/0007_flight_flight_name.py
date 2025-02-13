# Generated by Django 5.1.3 on 2025-02-09 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AirLine', '0006_remove_flight_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='flight_name',
            field=models.CharField(default='Null', max_length=100, verbose_name='Flight Name'),
            preserve_default=False,
        ),
    ]
