"""
Serializers for Travel Suite - REST API
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from django.conf import settings

from .models import (
    User, AdminProfile, OperatorProfile, Customer, Route, Vehicle,
    Seat, Event, Booking, Ticket, Payment, Transaction
)
from .utils import check_seat_availability, get_next_booking_id


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for User Registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    # Add fields for operator profile
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Add field for admin profile
    admin_license_number = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone_number', 
                  'national_id', 'is_admin', 'is_operator', 'first_name', 'last_name',
                  'company_name', 'license_number', 'admin_license_number']

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Validate operator-specific fields
        if data.get('is_operator'):
            if not data.get('company_name'):
                raise serializers.ValidationError({"company_name": "Company name is required for operators."})
            if not data.get('license_number'):
                raise serializers.ValidationError({"license_number": "License number is required for operators."})
        
        # Validate admin-specific fields
        if data.get('is_admin'):
            if not data.get('admin_license_number'):
                raise serializers.ValidationError({"admin_license_number": "License number is required for admins."})
        
        return data

    def create(self, validated_data):
        # Extract profile-specific data
        company_name = validated_data.pop('company_name', None)
        license_number = validated_data.pop('license_number', None)
        admin_license_number = validated_data.pop('admin_license_number', None)
        
        # Get national_id and convert empty string to None to avoid unique constraint violation
        national_id = validated_data.get('national_id', None)
        if national_id == '' or not national_id:
            national_id = None
        
        # Create the user
        # Operators start as inactive until admin approves them
        is_operator = validated_data.get('is_operator', False)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            national_id=national_id,  # Use None instead of empty string
            is_admin=validated_data.get('is_admin', False),
            is_operator=is_operator,
            is_active=False if is_operator else True,  # Operators need approval, admins are active by default
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.is_approved = False if is_operator else True
        user.save(update_fields=['is_approved', 'is_active'])
        
        # Create OperatorProfile if user is an operator
        # is_approved defaults to False, so operator needs admin approval
        if user.is_operator and company_name and license_number:
            OperatorProfile.objects.create(
                user=user,
                company_name=company_name,
                license_number=license_number,
                is_approved=False  # Requires admin approval
            )
        
        # Create AdminProfile if user is an admin
        if user.is_admin and admin_license_number:
            AdminProfile.objects.create(
                user=user,
                license_number=admin_license_number
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

        if user.is_superuser:
            data['user'] = user
            return data

        if user.is_admin:
            allowed = getattr(settings, 'AUTHORIZED_ADMIN_USERNAMES', [])
            if user.username not in allowed:
                raise serializers.ValidationError("Only authorized admins may log in.")
            data['user'] = user
            return data

        if user.is_operator:
            if not getattr(user, 'is_approved', False):
                raise serializers.ValidationError("Your account is pending admin approval. Please wait for approval before logging in.")
            try:
                user.operator_profile
            except OperatorProfile.DoesNotExist:
                raise serializers.ValidationError("Operator profile not found. Please contact support.")
            data['user'] = user
            return data

        raise serializers.ValidationError("Only authorized admins may log in.")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User Model."""
    company_name = serializers.SerializerMethodField()
    license_number = serializers.SerializerMethodField()
    is_approved = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'national_id', 'is_admin', 'is_operator', 'is_active',
                  'company_name', 'license_number', 'is_approved']
        read_only_fields = ['id']
    
    def get_company_name(self, obj):
        if hasattr(obj, 'operator_profile'):
            return obj.operator_profile.company_name
        return None
    
    def get_license_number(self, obj):
        if hasattr(obj, 'operator_profile'):
            return obj.operator_profile.license_number
        return None
    


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
        fields = ['id', 'user', 'company_name', 'license_number', 'is_approved']
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
    route_details = RouteSerializer(source='route', read_only=True)
    vehicle_details = VehicleSerializer(source='vehicle', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'customer', 'customer_name', 'event', 'route', 'route_details',
            'vehicle', 'vehicle_details', 'seat_number', 'seats_booked', 'amount',
            'status', 'travel_date', 'created_at', 'timestamp'
        ]
        read_only_fields = ['id', 'booking_id', 'created_at', 'timestamp']

    def validate(self, attrs):
        vehicle = attrs.get('vehicle') or getattr(self.instance, 'vehicle', None)
        route = attrs.get('route') or getattr(self.instance, 'route', None)
        travel_date = attrs.get('travel_date') or getattr(self.instance, 'travel_date', None)
        seats_booked = attrs.get('seats_booked') or getattr(self.instance, 'seats_booked', 1)

        if vehicle and not route:
            attrs['route'] = vehicle.route
            route = vehicle.route

        if vehicle and travel_date:
            available = check_seat_availability(vehicle, travel_date)
            if seats_booked > available and (not self.instance or seats_booked != self.instance.seats_booked):
                raise serializers.ValidationError(
                    {'seats_booked': f'Only {available} seats available for this vehicle on {travel_date}.'}
                )

        return attrs

    def create(self, validated_data):
        if not validated_data.get('booking_id'):
            validated_data['booking_id'] = get_next_booking_id()
        if not validated_data.get('route') and validated_data.get('vehicle'):
            validated_data['route'] = validated_data['vehicle'].route
        return super().create(validated_data)


class PublicBookingSerializer(serializers.Serializer):
    """Serializer for public client bookings."""
    customer_name = serializers.CharField(max_length=150)
    vehicle_id = serializers.PrimaryKeyRelatedField(source='vehicle', queryset=Vehicle.objects.select_related('route'))
    travel_date = serializers.DateField()
    seats_booked = serializers.IntegerField(min_value=1, default=1)
    payment_method = serializers.ChoiceField(choices=Payment._meta.get_field('payment_method').choices)
    payment_details = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        vehicle = attrs['vehicle']
        travel_date = attrs['travel_date']
        seats_booked = attrs.get('seats_booked', 1)
        available = check_seat_availability(vehicle, travel_date)
        if seats_booked > available:
            raise serializers.ValidationError(
                {'seats_booked': f'Only {available} seats available for this vehicle on {travel_date}.'}
            )
        return attrs


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
