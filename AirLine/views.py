from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import *
def login_interface(request):
    return render(request, 'login.html') 
def forget_password(request):
    return render(request, 'forget_pass.html') 
def admin(request):
    return render(request, 'Admin.html') 
def passenger(request):
    if request.method == 'POST':
        # Getting form data
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        nid = request.POST.get('nid')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        # Validation
        if not all([full_name, email, phone, nid, age, gender, password, confirm_password]):
            messages.error(request, "All fields are required!")
            return render(request, 'passenger.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'passenger.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'passenger.html')

        try:
            # Create User and Registration records
            user = User.objects.create_user(username=email, email=email, password=password)
            Registration.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                nid=nid,
                age=age,
                gender=gender
            )

            messages.success(request, "Registration successful!")
            return redirect('login')  # Replace 'login' with your login page's URL name
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return render(request, 'passenger.html')

    return render(request, 'passenger.html')
def buy_ticket(request):
    return render(request, 'Buy_ticket.html') 
def after_admin_login(request):
    return render(request, 'after_admin_login.html') 
def navbar(request):
    return render(request, 'navbar.html')     

