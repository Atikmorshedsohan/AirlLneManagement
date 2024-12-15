
from django.contrib import admin
from django.urls import path
from AirLine import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_interface, name='login'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('admin-panel/', views.admin, name='admin'),
    path('passenger/', views.passenger, name='passenger'),
    path('buy-ticket/', views.buy_ticket, name='buy_ticket'),
    path('after-admin-login/', views.after_admin_login, name='after_admin_login'),
    path('',views.navbar),
    path('passenger/',views.passenger, name='register_passenger'),
]
