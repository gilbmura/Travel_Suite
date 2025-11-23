from django.contrib import admin
from .models import ScheduleRecurrence, ScheduleOccurrence, Booking


@admin.register(ScheduleRecurrence)
class ScheduleRecurrenceAdmin(admin.ModelAdmin):
    list_display = ['route', 'bus', 'recurrence_type', 'departure_time', 'is_active', 'created_at']
    list_filter = ['recurrence_type', 'is_active', 'route']
    search_fields = ['route__name', 'bus__plate_number']


@admin.register(ScheduleOccurrence)
class ScheduleOccurrenceAdmin(admin.ModelAdmin):
    list_display = ['recurrence', 'date', 'departure_time', 'status', 'remaining_seats', 'created_at']
    list_filter = ['status', 'date', 'recurrence__route']
    search_fields = ['recurrence__route__name']
    readonly_fields = ['remaining_seats', 'time_to_departure']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'passenger_name', 'phone_number', 'schedule_occurrence', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['passenger_name', 'phone_number', 'id']
    readonly_fields = ['id', 'created_at', 'cancelled_at']

