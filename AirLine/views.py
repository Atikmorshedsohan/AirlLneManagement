import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404,JsonResponse
from django.db import transaction, models
from django.db.models import Q
from .forms import PassengerForm
from .models import Airport, Flight, Registration,ContactMessage,Ticket
from django.core.mail import send_mail
from datetime import datetime




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

def buy_ticket(request):
    if request.method == 'POST':
        try:
            source_airport_id = request.POST.get('source_airport')
            destination_airport_id = request.POST.get('destination_airport')
            departure_date = request.POST.get('departure_date')
            num_passengers = int(request.POST.get('num_passengers'))
            ticket_class = request.POST.get('ticket_class')
            contact_email = request.POST.get('contact_email')

            source_airport = get_object_or_404(Airport, id=source_airport_id)
            destination_airport = get_object_or_404(Airport, id=destination_airport_id)

            flight = Flight.objects.filter(
                source_airport=source_airport,
                destination_airport=destination_airport,
                date=departure_date
            ).first()

            if not flight:
                messages.error(request, "No flight found.")
                return redirect('buy_ticket')

            ticket_price = {
                'Economy': flight.economy_price,
                'Business': flight.business_price,
                'First': flight.first_class_price
            }.get(ticket_class, 0)

            tickets_created = []
            with transaction.atomic():
                for _ in range(num_passengers):
                    ticket = Ticket.objects.create(
                        flight=flight,
                        email=contact_email,
                        ticket_class=ticket_class,
                        price=ticket_price,
                        status="Pending Approval"
                    )
                    tickets_created.append(ticket.id)  # Store ticket IDs for debugging

            messages.success(request, f"Tickets booked! Ticket IDs: {tickets_created}")
            return redirect('ticket_success', flight_id=flight.id, num_tickets=num_passengers)

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('buy_ticket')

    airports = Airport.objects.all()
    return render(request, 'buy_ticket.html', {'airports': airports})


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
                'time': flight.time.strftime('%H:%M'),
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


def ticket_success(request, flight_id, num_tickets):
    # Ensure flight exists
    flight = get_object_or_404(Flight, id=flight_id)

    return render(request, "ticket_success.html", {
        "flight": flight,
        "num_tickets": num_tickets
    })



def seat_selection(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    seats = flight.seats.all()
    return render(request, 'seat_selection.html', {'flight': flight, 'seats': seats})
