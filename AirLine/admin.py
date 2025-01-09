from django.contrib import admin
from .models import Flight, Registration,ContactMessage,Airport

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'nid', 'age', 'gender','username')
    search_fields = ('full_name', 'email', 'phone', 'nid')
    list_filter = ('gender', 'age')
    ordering = ('full_name',)

admin.site.register(Registration, RegistrationAdmin)
@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'code')  # Display these fields in the admin list view
    search_fields = ('name', 'city', 'country', 'code')  # Enable search for these fields
    list_filter = ('country',)  # Add a filter for the country
    ordering = ('city', 'name')  # Order airports by city and name

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('flight_number', 'source_airport', 'destination_airport', 'date', 'time', 'available_seats', 'price', 'created_at')

    # Search functionality
    search_fields = ('flight_number', 'source_airport__name', 'destination_airport__name', 'source_airport__code', 'destination_airport__code')

    # Filters for easy navigation
    list_filter = ('source_airport', 'destination_airport', 'date')

    # Fields to be editable directly in the list view
    list_editable = ('available_seats', 'price')

    # Fields to display on the detail/edit page
    fields = ('flight_number', 'source_airport', 'destination_airport', 'date', 'time', 'available_seats', 'price', 'created_at', 'updated_at')

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')

    # Order by date and time by default
    ordering = ['date', 'time']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')  # Fields to display in the admin list view
    list_filter = ('submitted_at',)  # Filter messages by submission date
    search_fields = ('name', 'email', 'message')  # Add search functionality for these fields
    ordering = ('-submitted_at',)  # Order messages by latest first
    readonly_fields = ('submitted_at',)  # Make submitted_at field read-only
