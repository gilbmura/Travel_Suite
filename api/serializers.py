from rest_framework import serializers
from routes.models import District, Route
from buses.models import Bus
from bookings.models import ScheduleRecurrence, ScheduleOccurrence, Booking
from payments.models import PaymentTransaction, Refund
from operators.models import OperatorUser, OperatorAssignment


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'code']


class RouteSerializer(serializers.ModelSerializer):
    origin = DistrictSerializer(read_only=True)
    destination = DistrictSerializer(read_only=True)
    origin_id = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), source='origin', write_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), source='destination', write_only=True)
    
    class Meta:
        model = Route
        fields = ['id', 'name', 'origin', 'destination', 'origin_id', 'destination_id', 
                  'distance_km', 'estimated_duration_minutes', 'fare', 'is_active']


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'plate_number', 'capacity', 'company_name', 'is_active']


class ScheduleOccurrenceSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    bus = BusSerializer(read_only=True, source='recurrence.bus')
    remaining_seats = serializers.IntegerField(read_only=True)
    time_to_departure = serializers.IntegerField(read_only=True, allow_null=True)
    
    class Meta:
        model = ScheduleOccurrence
        fields = ['id', 'recurrence', 'date', 'departure_time', 'arrival_time', 
                  'status', 'route', 'bus', 'remaining_seats', 'time_to_departure']


class BookingSerializer(serializers.ModelSerializer):
    schedule_occurrence = ScheduleOccurrenceSerializer(read_only=True)
    schedule_occurrence_id = serializers.PrimaryKeyRelatedField(
        queryset=ScheduleOccurrence.objects.all(), 
        source='schedule_occurrence', 
        write_only=True
    )
    
    class Meta:
        model = Booking
        fields = ['id', 'passenger_name', 'phone_number', 'email', 'schedule_occurrence', 
                  'schedule_occurrence_id', 'payment_method', 'status', 'created_at', 
                  'cancelled_at', 'refund_id']
        read_only_fields = ['id', 'status', 'created_at', 'cancelled_at', 'refund_id']


class BookingCreateSerializer(serializers.ModelSerializer):
    schedule_occurrence_id = serializers.IntegerField()
    
    class Meta:
        model = Booking
        fields = ['passenger_name', 'phone_number', 'email', 'schedule_occurrence_id', 'payment_method']


class BookingStatusSerializer(serializers.ModelSerializer):
    schedule_occurrence = ScheduleOccurrenceSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'passenger_name', 'phone_number', 'email', 'schedule_occurrence', 
                  'payment_method', 'status', 'created_at', 'cancelled_at', 'refund_id']


class OperatorUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = OperatorUser
        fields = ['id', 'username', 'full_name', 'phone_number', 'email', 'is_active']


class ScheduleRecurrenceSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    bus = BusSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), source='route', write_only=True)
    bus_id = serializers.PrimaryKeyRelatedField(queryset=Bus.objects.all(), source='bus', write_only=True)
    
    class Meta:
        model = ScheduleRecurrence
        fields = ['id', 'route', 'route_id', 'bus', 'bus_id', 'recurrence_type', 
                  'departure_time', 'arrival_time', 'is_active', 'created_at']


class OperatorAssignmentSerializer(serializers.ModelSerializer):
    operator = OperatorUserSerializer(read_only=True)
    route = RouteSerializer(read_only=True)
    operator_id = serializers.PrimaryKeyRelatedField(queryset=OperatorUser.objects.all(), source='operator', write_only=True)
    route_id = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all(), source='route', write_only=True)
    
    class Meta:
        model = OperatorAssignment
        fields = ['id', 'operator', 'operator_id', 'route', 'route_id', 'is_active', 'created_at']

