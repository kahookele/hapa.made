from django.contrib import admin
from .models import Workshop, Booking

class WorkshopAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'price', 'seats_available', 'difficulty']
    list_filter = ['difficulty', 'date']
    search_fields = ['title', 'description', 'location']
    ordering = ['-date']

class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'workshop', 'payment_status']
    list_filter = ['payment_status', 'workshop']
    search_fields = ['name', 'email', 'phone']

admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(Booking, BookingAdmin)
