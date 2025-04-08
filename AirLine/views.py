import json
import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.db import transaction, models
from django.db.models import Q,Sum
from .forms import PassengerForm
from .models import Airport, Flight, Registration, ContactMessage, Ticket
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
#For pdf

from django.template.loader import get_template
from xhtml2pdf import pisa


def generate_ticket_pdf(request, booking_reference):
    """Generate and return a flight ticket PDF."""
    tickets = Ticket.objects.filter(booking_reference=booking_reference)
    
    if not tickets.exists():
        return HttpResponse("No ticket found", status=404)
    
    first_ticket = tickets.first()
    
    template_path = 'ticket_pdf.html'
    context = {'ticket': first_ticket}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking_reference}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    return response



def ticket_details(request, booking_reference):
    tickets = Ticket.objects.filter(booking_reference=booking_reference).select_related('flight')

    if not tickets.exists():
        messages.error(request, "No ticket found.")
        return redirect('buy_ticket')

    first_ticket = tickets.first()
    flight = first_ticket.flight if first_ticket else None

    ticket_info = {
        'passenger_name': first_ticket.passenger_name,
        'email': first_ticket.email,
        'flight_number': getattr(flight, 'flight_number', "N/A"),
        'flight_name': getattr(flight, 'flight_name', "N/A"),
        'source': getattr(flight.source_airport, 'name', "Unknown") if flight else "Unknown",
        'destination': getattr(flight.destination_airport, 'name', "Unknown") if flight else "Unknown",
        'ticket_class': first_ticket.ticket_class,
        'price_per_ticket': first_ticket.price,
        'num_seats': tickets.count(),
        'total_price': tickets.aggregate(total=Sum('price'))['total'] or 0,
        'booking_reference': first_ticket.booking_reference,  # ✅ Ensure this is set
    }

    return render(request, 'ticket_details.html', {'ticket': ticket_info})




def login_interface(request):
    if request.method == 'POST':
        # Retrieve data from the form
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user if authentication is successful
            login(request, user)
            return redirect('dashboard')  # Redirect to a dashboard or home page
        else:
            # Show an error message if authentication fails
            messages.error(request, 'Invalid username or password.')
            return redirect('login')  # Redirect back to login page on failure

    # Render the login form for GET requests
    return render(request, 'login.html')


def registration(request):
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Get username from the form
            email = form.cleaned_data.get('email')
            full_name = form.cleaned_data.get('full_name')
            phone = form.cleaned_data.get('phone')
            nid = form.cleaned_data.get('nid')
            age = form.cleaned_data.get('age')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')

            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken. Please choose a different one.")
                return render(request, 'registration.html', {'form': form})

            try:
                with transaction.atomic():
                    # Create the User
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()

                    # Create the Registration profile
                    registration = Registration.objects.create(
                        user=user,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        nid=nid,
                        age=age,
                        gender=gender
                    )
                    registration.save()

                messages.success(request, "Your account has been created successfully.")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = PassengerForm()

    return render(request, 'registration.html', {'form': form})

def profile_view(request):
    user = request.user
    try:
        profile = user.profile  # Access the related Profile model
    except AttributeError:
        profile = None

    context = {
        'profile': {
            'full_name': user.get_full_name(),
            'email': user.email,
            # 'phone': profile.phone if profile else 'Not Provided',
            # 'nid': profile.nid if profile else 'Not Provided',
            # 'age': profile.age if profile else 'Not Provided',
            # 'get_gender_display': profile.get_gender_display() if profile else 'Not Provided',
            'username': user.username,
        }
    }
    return render(request, 'profile.html', context)


def dashboard(request):
    flights = Flight.objects.all()
    print(flights)  # Print the queryset in the console
    return render(request, 'dashboard.html', {'flights': flights})



def payment_page(request):
    ticket = Ticket.objects.first()  # Fetches the first available ticket

    if not ticket:
        return render(request, 'error.html', {'message': "No tickets available."})

    context = {
        'ticket': {
            'passenger_name': ticket.passenger_name,
            'email': ticket.email,
            'flight_number': ticket.flight.flight_number,
            'source': ticket.flight.source_airport.name,
            'destination': ticket.flight.destination_airport.name,
            'ticket_class': ticket.ticket_class,
            'price': ticket.price,
            'booking_reference': ticket.booking_reference,
            'payment_status': ticket.payment_status,
        }
    }

    return render(request, 'payment_page.html', context)


def fingerprint_scan(request):
    # This would be where you handle fingerprint logic, for now just render a page
    # if request.method == 'POST':
        # Logic for handling the fingerprint data can go here
        # return redirect('boarding_pass')  # Assuming there’s a boarding pass view

    return render(request, 'fingerprint_scan.html')


def admin_approve_ticket(request, ticket_id):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized action.")
        return redirect('admin_dashboard')

    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = "Approved"
    ticket.save()

    messages.success(request, "Ticket approved successfully!")
    return redirect('admin_dashboard')


def navbar(request):
    return render(request, 'navbar.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save the data to the database
        ContactMessage.objects.create(name=name, email=email, message=message)
        
        # Redirect to the success page with the name passed as context
        return render(request, 'contact_success.html', {'name': name})
    
    return render(request, 'contact.html')



def contact_success(request):
    return render(request, 'contact_success.html')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')  # Redirect to the profile page after successful password change

    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully updated!")
        return super().form_valid(form)


def about_us(request):
    return render(request, 'about_us.html') 




def search_flights(request):
    if request.method == 'GET' and not request.GET.get('from'):
        return render(request, 'flight_search.html')

    source = request.GET.get('from', '').strip()
    destination = request.GET.get('to', '').strip()
    date = request.GET.get('date', '').strip()

    # Validate input fields
    if not source or not destination or not date:
        return JsonResponse({'message': 'Please provide source, destination, and date.'}, status=400)

    try:
        # Validate date format
        date = datetime.strptime(date, '%Y-%m-%d').date()

        # Search flights by airport codes
        flights = Flight.objects.filter(
            source_airport__city__iexact=source,  # Using source city
            destination_airport__city__iexact=destination,  # Using destination city
            date=date
        )


        # Check if flights exist
        if not flights.exists():
            return JsonResponse({'message': 'No flights found for the given source, destination, and date.'}, status=404)

        # Format the flight data for the response
        flight_list = [
            {
                'id': flight.id,
                'flight_number': flight.flight_number,
                'source': flight.source_airport.name,
                'destination': flight.destination_airport.name,
                'date': flight.date.strftime('%Y-%m-%d'),
                'arrival_time': flight.time.strftime('%H:%M'),
                'available_seats': flight.available_seats,
                'economy_price': float(flight.economy_price),
                'business_price': float(flight.business_price),
                'first_class_price': float(flight.first_class_price),
            }
            for flight in flights
        ]

        # Return the search results as JSON
        return JsonResponse(flight_list, safe=False)

    except ValueError:
        # Date parsing issue
        return JsonResponse({'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
    except Exception as e:
        # Generic exception handler
        print(f"Unexpected error: {e}")
        return JsonResponse({'message': 'An internal error occurred.'}, status=500)



def search2(request):
    if request.method == 'GET' and not request.GET.get('from'):
        return render(request, 'search2.html')

    source = request.GET.get('from', '').strip()
    destination = request.GET.get('to', '').strip()
    date = request.GET.get('date', '').strip()

    if not source or not destination or not date:
        return JsonResponse({'message': 'Please provide source, destination, and date.'}, status=400)

    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
        flights = Flight.objects.filter(
            source_airport__city__iexact=source,
            destination_airport__city__iexact=destination,
            date=date
        )

        if not flights.exists():
            return JsonResponse({'message': 'No flights found for the given source, destination, and date.'}, status=404)

        # Instead of redirecting, render a template and pass all flights
        return render(request, 'flight_show.html', {'flights': flights})

    except ValueError:
        return JsonResponse({'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({'message': 'An internal error occurred.'}, status=500)




def buy_ticket(request):
    airports = Airport.objects.all()

    # Handle POST request
    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        flight = get_object_or_404(Flight, id=flight_id)

        source_id = flight.source_airport.id
        destination_id = flight.destination_airport.id
        departure_date = request.POST.get('departure_date')  # Get the date from the form submission

        # You can also use `flight.date` if you want to ensure the date is exactly what you expect
        # But since we're getting the date from the form, this is enough.

        passenger_name = request.POST.get('passenger_name')
        email = request.POST.get('email')
        ticket_class = request.POST.get('ticket_class')
        num_seats = int(request.POST.get('num_seats'))

        if source_id == destination_id:
            messages.error(request, "Source and destination cannot be the same.")
            return redirect('buy_ticket')

        if num_seats > flight.available_seats:
            messages.error(request, f"Only {flight.available_seats} seat(s) available for this flight.")
            return redirect('buy_ticket')

        price_mapping = {
            "Economy": flight.economy_price,
            "Business": flight.business_price,
            "First": flight.first_class_price
        }
        price_per_ticket = price_mapping.get(ticket_class, flight.economy_price)
        total_price_value = price_per_ticket * num_seats

        flight.available_seats -= num_seats
        flight.save()

        shared_booking_reference = uuid.uuid4().hex[:20]

        tickets = []
        for _ in range(num_seats):
            ticket = Ticket(
                flight=flight,
                passenger_name=passenger_name,
                email=email,
                ticket_class=ticket_class,
                price=total_price_value,
                booking_reference=shared_booking_reference,
            )
            ticket.save()
            tickets.append(ticket)

        return redirect('ticket_details', booking_reference=shared_booking_reference)

    # Handle GET request to show the flight details and available dates
    flight_id = request.GET.get('flight_id')
    flight = Flight.objects.get(id=flight_id) if flight_id else None

    # Fetch all available dates for the selected flight (example query)
    available_dates = Flight.objects.filter(
        source_airport=flight.source_airport,
        destination_airport=flight.destination_airport
    ).values_list('date', flat=True).distinct()

    context = {
        'airports': airports,
        'flight_id': flight_id,
        'prefilled_source': flight.source_airport.id if flight else '',
        'prefilled_destination': flight.destination_airport.id if flight else '',
        'prefilled_date': flight.date if flight else '',
        'available_dates': available_dates,
    }

    return render(request, 'buy_ticket.html', context)










def flight_show(request, flight_id):
    """Handles flight ticket booking and displays the selected flight"""
    flight = get_object_or_404(Flight, id=flight_id)

    # Get values from query parameters (if available)
    source = request.GET.get('source', flight.source_airport.city)
    destination = request.GET.get('destination', flight.destination_airport.city)
    date = request.GET.get('date', flight.date)

    context = {
        'flights': [flight],
        'source': source,
        'destination': destination,
        'date': date,
    }

    return render(request, 'flight_show.html', context)

    