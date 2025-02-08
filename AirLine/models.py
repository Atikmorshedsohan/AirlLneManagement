import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Registration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15)
    nid = models.CharField(max_length=20)
    age = models.PositiveIntegerField()

    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name

    # Accessor for the username
    @property
    def username(self):
        return self.user.username

    # Accessor for the password
    @property
    def password(self):
        return self.user.password

class Airport(models.Model):
    name = models.CharField(max_length=100, verbose_name="Airport Name")
    city = models.CharField(max_length=100, verbose_name="City")
    country = models.CharField(max_length=100, verbose_name="Country")
    code = models.CharField(max_length=10, unique=True, verbose_name="Airport Code (IATA/ICAO)")

    def __str__(self):
        return self.name  # Changed from f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Airport"
        verbose_name_plural = "Airports"
        ordering = ['city', 'name']


class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True, verbose_name="Flight Number")
    source_airport = models.ForeignKey(Airport, related_name="departing_flights", on_delete=models.CASCADE, verbose_name="Source Airport")
    destination_airport = models.ForeignKey(Airport, related_name="arriving_flights", on_delete=models.CASCADE, verbose_name="Destination Airport")
    date = models.DateField(verbose_name="Flight Date")
    time = models.TimeField(verbose_name="Flight Time")
    available_seats = models.PositiveIntegerField(default=50, verbose_name="Available Seats")
    economy_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Economy Class Price")
    business_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Business Class Price")
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="First Class Price")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    def __str__(self):
        return f"{self.flight_number} ({self.source_airport.code} → {self.destination_airport.code})"

    class Meta:
        verbose_name = "Flight"
        verbose_name_plural = "Flights"
        ordering = ['date', 'time']


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Removed', 'Removed'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, verbose_name="Flight")
    passenger_name = models.CharField(max_length=100, verbose_name="Passenger Name")
    email = models.EmailField(verbose_name="Email")
    contact_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Contact Phone")
    ticket_class = models.CharField(
        max_length=20,
        choices=[('Economy', 'Economy'), ('Business', 'Business'), ('First', 'First')],
        verbose_name="Ticket Class"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ticket Price")
    booked_at = models.DateTimeField(auto_now_add=True, verbose_name="Booked At")
    booking_reference = models.CharField(max_length=20, unique=True, verbose_name="Booking Reference")
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending',
        verbose_name="Payment Status"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Approval Status")

    def save(self, *args, **kwargs):
        """Generate a unique booking reference before saving."""
        if not self.booking_reference:
            self.booking_reference = uuid.uuid4().hex[:20]  # More reliable unique value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket: {self.passenger_name} ({self.flight.flight_number}) - {self.status} - {self.payment_status}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    