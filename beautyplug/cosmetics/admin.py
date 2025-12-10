from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Appointment, Client, ContactMessage, Service, Booking



# Register your models here.
admin.site.register(Service)
admin.site.register(ContactMessage)
admin.site.register(Booking)
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    actions = ['approve_clients', 'reject_clients']
      
def approve_clients(self, request, queryset):
            for client in queryset:
                client.approve(user=request.user)
            self.message_user(request, f"{queryset.count()} clients approved.") 

# class BookingAdmin(admin.ModelAdmin):
#     list_display = ('id', 'client', 'get_services', 'date', 'time', 'total_price', 'status', 'created_at')
#     list_filter = ('status', 'date')
#     search_fields = ('client__username',)
#     ordering = ('-created_at',)

#     def get_services(self, obj):
#         return ", ".join([service.name for service in obj.services.all()])
#     get_services.short_description = "Services"  

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'display_services', 'date', 'time', 'total_price', 'status')
    list_filter = ('status', 'date')
    search_fields = ('client__username',)
    ordering = ('-date', '-time')

    # Custom method to display only selected services
    def display_services(self, obj):
        return ", ".join([service.name for service in obj.services.all()])
    display_services.short_description = 'Services'

