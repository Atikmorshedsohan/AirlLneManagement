from django.contrib import admin
from .models import Flight, Registration, ContactMessage, Airport, Ticket

# Admin for Registration
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'nid', 'age', 'gender', 'username')  
    search_fields = ('full_name', 'email', 'phone', 'nid')  
    list_filter = ('gender', 'age')  
    ordering = ('full_name',)  

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'code')
    search_fields = ('name', 'city', 'country', 'code')
    ordering = ('city', 'name')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "flight_name", "source_airport", "destination_airport", "date", "departure_time", "arrival_time")  # Removed 'time'
    list_filter = ('source_airport', 'destination_airport', 'date')
    search_fields = ('flight_number', 'source_airport__name', 'destination_airport__name')
    ordering = ["date", "departure_time","arrival_time"] 

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('flight', 'passenger_name', 'ticket_class', 'price', 'status', 'booked_at')
    list_filter = ('ticket_class', 'status', 'booked_at')
    search_fields = ('passenger_name', 'email', 'booking_reference')
    ordering = ('-booked_at',)
    actions = ['approve_tickets', 'remove_tickets']

    @admin.action(description='Approve selected tickets')
    def approve_tickets(self, request, queryset):
        updated = queryset.update(status="Approved")
        self.message_user(request, f"{updated} ticket(s) successfully approved.")

    @admin.action(description='Remove selected tickets')
    def remove_tickets(self, request, queryset):
        updated = queryset.update(status="Removed")
        self.message_user(request, f"{updated} ticket(s) removed.")

# Admin for ContactMessage
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')  
    list_filter = ('submitted_at',)  
    search_fields = ('name', 'email', 'message')  
    ordering = ('-submitted_at',)  
    readonly_fields = ('submitted_at',)  
