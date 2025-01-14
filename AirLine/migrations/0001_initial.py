# Generated by Django 5.1.3 on 2025-01-07 16:59

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Airport Name')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('country', models.CharField(max_length=100, verbose_name='Country')),
                ('code', models.CharField(max_length=10, unique=True, verbose_name='Airport Code (IATA/ICAO)')),
            ],
            options={
                'verbose_name': 'Airport',
                'verbose_name_plural': 'Airports',
                'ordering': ['city', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=20, unique=True, verbose_name='Flight Number')),
                ('date', models.DateField(verbose_name='Flight Date')),
                ('time', models.TimeField(verbose_name='Flight Time')),
                ('available_seats', models.PositiveIntegerField(default=50, verbose_name='Available Seats')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ticket Price (USD)')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('destination_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arriving_flights', to='AirLine.airport', verbose_name='Destination Airport')),
                ('source_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departing_flights', to='AirLine.airport', verbose_name='Source Airport')),
            ],
            options={
                'verbose_name': 'Flight',
                'verbose_name_plural': 'Flights',
                'ordering': ['date', 'time'],
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('nid', models.CharField(max_length=20)),
                ('age', models.PositiveIntegerField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
