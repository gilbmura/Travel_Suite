"""
Django Admin Configuration for Travel Suite
"""

from django.contrib import admin
from .models import (
    User, AdminProfile, OperatorProfile, Customer, Route, Vehicle,
    Seat, Event, Booking, Ticket, Payment, Transaction
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_admin', 'is_operator', 'is_active']
    list_filter = ['is_admin', 'is_operator', 'is_active']
    search_fields = ['username', 'email', 'phone_number']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Contact', {'fields': ('phone_number', 'national_id')}),
        ('Permissions', {'fields': ('is_admin', 'is_operator', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'license_number']
    search_fields = ['user__username', 'license_number']


@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'license_number']
    search_fields = ['company_name', 'user__username', 'license_number']
    list_filter = ['company_name']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'national_id', 'created_at']
    search_fields = ['name', 'phone_number', 'national_id']
    list_filter = ['created_at']
    fieldsets = (
        ('Personal Information', {'fields': ('name', 'phone_number', 'national_id')}),
        ('Address', {'fields': ('address',)}),
        ('Timestamps', {'fields': ('created_at', 'timestamp'), 'classes': ('collapse',)}),
    )


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['origin', 'destination', 'departure_time', 'arrival_time', 'fare']
    search_fields = ['origin', 'destination']
    list_filter = ['departure_time', 'fare']
    fieldsets = (
        ('Route Information', {'fields': ('origin', 'destination')}),
        ('Timing', {'fields': ('departure_time', 'arrival_time')}),
        ('Details', {'fields': ('stops', 'fare')}),
        ('Timestamps', {'fields': ('created_at', 'timestamp'), 'classes': ('collapse',)}),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'route', 'capacity', 'status']
    search_fields = ['license_plate']
    list_filter = ['status', 'route']
    fieldsets = (
        ('Vehicle Information', {'fields': ('license_plate', 'capacity')}),
        ('Assignment', {'fields': ('route',)}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'timestamp'), 'classes': ('collapse',)}),
    )


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'seat_number', 'is_booked']
    search_fields = ['vehicle__license_plate', 'seat_number']
    list_filter = ['is_booked', 'vehicle']
    fieldsets = (
        ('Seat Information', {'fields': ('vehicle', 'seat_number')}),
        ('Booking Status', {'fields': ('is_booked', 'booking')}),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'available_seats']
    search_fields = ['name', 'location']
    list_filter = ['date', 'location']
    fieldsets = (
        ('Event Information', {'fields': ('name', 'date', 'location', 'available_seats')}),
        ('Timestamps', {'fields': ('created_at', 'timestamp'), 'classes': ('collapse',)}),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date', 'status', 'amount']
    search_fields = ['customer__name', 'id']
    list_filter = ['status', 'date']
    fieldsets = (
        ('Booking Information', {'fields': ('customer', 'event', 'route')}),
        ('Seat & Amount', {'fields': ('seat_number', 'amount')}),
        ('Status', {'fields': ('status', 'date')}),
        ('Timestamps', {'fields': ('created_at', 'timestamp'), 'classes': ('collapse',)}),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'is_used', 'validated_at']
    search_fields = ['qr_code', 'booking__id']
    list_filter = ['is_used', 'validated_at']
    fieldsets = (
        ('Ticket Information', {'fields': ('booking', 'qr_code')}),
        ('Validation', {'fields': ('is_used', 'validated_at')}),
    )
    readonly_fields = ['qr_code']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'payment_method', 'status']
    search_fields = ['booking__id']
    list_filter = ['status', 'payment_method', 'timestamp']
    fieldsets = (
        ('Payment Information', {'fields': ('booking', 'amount')}),
        ('Payment Method', {'fields': ('payment_method',)}),
        ('Status', {'fields': ('status',)}),
        ('Timestamp', {'fields': ('timestamp',), 'classes': ('collapse',)}),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'booking', 'amount', 'payment_status']
    search_fields = ['payment__id', 'booking__id']
    list_filter = ['payment_status', 'timestamp']
    fieldsets = (
        ('Transaction Information', {'fields': ('payment', 'booking', 'amount')}),
        ('Status', {'fields': ('payment_status',)}),
        ('Timestamp', {'fields': ('timestamp',), 'classes': ('collapse',)}),
    )
