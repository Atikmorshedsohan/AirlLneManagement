from django.contrib import admin
from .models import Registration

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'nid', 'age', 'gender')
    search_fields = ('full_name', 'email', 'phone', 'nid')
    list_filter = ('gender', 'age')
    ordering = ('full_name',)

admin.site.register(Registration, RegistrationAdmin)
