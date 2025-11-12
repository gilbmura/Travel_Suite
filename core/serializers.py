"""
Serializers for Travel Suite - REST API
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import (
    User, AdminProfile, OperatorProfile, Customer, Route, Vehicle, 
    Seat, Event, Booking, Ticket, Payment, Transaction
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for User Registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone_number', 
                  'national_id', 'is_admin', 'is_operator', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            national_id=validated_data.get('national_id', ''),
            is_admin=validated_data.get('is_admin', False),
            is_operator=validated_data.get('is_operator', False),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for User Login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User Model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'national_id', 'is_admin', 'is_operator', 'is_active']
        read_only_fields = ['id']


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for AdminProfile Model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = AdminProfile
        fields = ['id', 'user', 'license_number']
        read_only_fields = ['id']


class OperatorProfileSerializer(serializers.ModelSerializer):
    """Serializer for OperatorProfile Model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = OperatorProfile
        fields = ['id', 'user', 'company_name', 'license_number']
        read_only_fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer Model."""
    class Meta:
        model = Customer
        fields = ['id', 'name', 'address', 'phone_number', 'national_id', 
                  'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']


class RouteSerializer(serializers.ModelSerializer):
    """Serializer for Route Model."""
    class Meta:
        model = Route
        fields = ['id', 'origin', 'destination', 'departure_time', 'arrival_time', 
                  'stops', 'fare', 'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']


class SeatSerializer(serializers.ModelSerializer):
    """Serializer for Seat Model."""
    vehicle_license = serializers.CharField(source='vehicle.license_plate', read_only=True)

    class Meta:
        model = Seat
        fields = ['id', 'vehicle', 'vehicle_license', 'seat_number', 'is_booked', 'booking']
        read_only_fields = ['id']


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer for Vehicle Model."""
    seats = SeatSerializer(many=True, read_only=True)
    route_details = RouteSerializer(source='route', read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'license_plate', 'route', 'route_details', 'capacity', 
                  'status', 'seats', 'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event Model."""
    class Meta:
        model = Event
        fields = ['id', 'name', 'date', 'location', 'available_seats', 
                  'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking Model."""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    route_details = RouteSerializer(source='route', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True, allow_null=True)

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'customer_name', 'event', 'event_name', 'route', 
                  'route_details', 'seat_number', 'amount', 'status', 'date', 
                  'created_at', 'timestamp']
        read_only_fields = ['id', 'created_at', 'timestamp']


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket Model."""
    booking_details = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'booking', 'booking_details', 'qr_code', 'is_used', 'validated_at']
        read_only_fields = ['id', 'qr_code']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment Model."""
    booking_details = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'booking_details', 'amount', 'payment_method', 
                  'status', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction Model."""
    payment_details = PaymentSerializer(source='payment', read_only=True)
    booking_details = BookingSerializer(source='booking', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'payment', 'payment_details', 'booking', 'booking_details', 
                  'amount', 'payment_status', 'timestamp']
        read_only_fields = ['id', 'timestamp']
