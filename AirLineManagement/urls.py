from django.contrib import admin
from django.urls import path, include
from AirLine import views
from django.contrib.auth import views as auth_views
from AirLine.views import profile_view, CustomPasswordChangeView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Authentication views
    path('login/', views.login_interface, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.registration, name='register'),
    
    # Profile and password management
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),
    path('forget-password/', auth_views.PasswordResetView.as_view(template_name='forget_password.html'), name='password_reset'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # Core functionalities
    path('', views.navbar, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buy-ticket/', views.buy_ticket, name='buy_ticket'),
   # path('ticket-success/<int:flight_id>/<int:num_tickets>/', views.ticket_success, name='ticket_success'),
    path('contact/', views.contact, name='contact'),
    path('contact_success/',views.contact_success,name='contact_success.html'),
    path('about_us/', views.about_us, name='about_us'),   
    path('search-flights/', views.search_flights, name='search-flights'),
    path('ticket/<str:booking_reference>/', views.ticket_details, name='ticket_details'),
    path('payment/', views.payment_page, name='payment_page'),
    path('fingerprint-scan/', views.fingerprint_scan, name='fingerprint_scan'),
    
    
]
