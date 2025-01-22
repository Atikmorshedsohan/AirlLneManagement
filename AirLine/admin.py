from django.contrib import admin
from .models import Flight, Registration, ContactMessage, Airport,Ticket,Seat


# Admin for Registration
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'nid', 'age', 'gender', 'username')  # Fields to display in the admin list
    search_fields = ('full_name', 'email', 'phone', 'nid')  # Enable search functionality
    list_filter = ('gender', 'age')  # Add filters for gender and age
    ordering = ('full_name',)  # Order by full name


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'code')
    search_fields = ('name', 'city', 'country', 'code')
    ordering = ('city', 'name')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'source_airport', 'destination_airport', 'date', 'time', 'available_seats')
    list_filter = ('source_airport', 'destination_airport', 'date')
    search_fields = ('flight_number', 'source_airport__name', 'destination_airport__name')
    ordering = ['date', 'time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('flight', 'seat_number', 'is_sold')
    list_filter = ('is_sold', 'flight')
    search_fields = ('seat_number',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('flight', 'passenger_name', 'seat', 'ticket_class', 'price', 'is_approved', 'booked_at')
    list_filter = ('ticket_class', 'is_approved', 'booked_at')
    search_fields = ('passenger_name', 'email')
    ordering = ('-booked_at',)
    actions = ['approve_tickets']

    # Custom action to approve selected tickets
    @admin.action(description='Approve selected tickets')
    def approve_tickets(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} ticket(s) successfully approved.")

# Admin for ContactMessage
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')  # Fields to display in the admin list
    list_filter = ('submitted_at',)  # Add a filter for submission date
    search_fields = ('name', 'email', 'message')  # Enable search functionality
    ordering = ('-submitted_at',)  # Order messages by latest submission first
    readonly_fields = ('submitted_at',)  # Make the submitted_at field read-only
