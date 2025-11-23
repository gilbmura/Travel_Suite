"""
Admin-specific views for full CRUD operations.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, time

from routes.models import District, Route
from buses.models import Bus
from bookings.models import ScheduleRecurrence, ScheduleOccurrence, Booking
from operators.models import OperatorUser, OperatorAssignment
from payments.models import PaymentTransaction, Refund
from accounts.models import User

from .serializers import (
    DistrictSerializer, RouteSerializer, BusSerializer,
    ScheduleOccurrenceSerializer, BookingSerializer, ScheduleRecurrenceSerializer
)


def admin_dashboard_view(request):
    """Admin dashboard with full management capabilities."""
    if not request.user.is_authenticated:
        return redirect('admin-login')
    
    if not (request.user.is_staff or request.user.is_superuser):
        logout(request)
        return redirect('admin-login')
    
    return render(request, 'admin/dashboard.html')


# District Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_districts(request):
    """List or create districts."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        districts = District.objects.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = DistrictSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'PUT', 'DELETE'])
def admin_district_detail(request, pk):
    """Get, update, or delete a district."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    district = get_object_or_404(District, pk=pk)
    
    if request.method == 'GET':
        serializer = DistrictSerializer(district)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = DistrictSerializer(district, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        district.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Route Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_routes(request):
    """List or create routes."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        routes = Route.objects.select_related('origin', 'destination').all()
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'PUT', 'DELETE'])
def admin_route_detail(request, pk):
    """Get, update, or delete a route."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    route = get_object_or_404(Route, pk=pk)
    
    if request.method == 'GET':
        serializer = RouteSerializer(route)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = RouteSerializer(route, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Bus Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_buses(request):
    """List or create buses."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        buses = Bus.objects.all()
        serializer = BusSerializer(buses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'PUT', 'DELETE'])
def admin_bus_detail(request, pk):
    """Get, update, or delete a bus."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    bus = get_object_or_404(Bus, pk=pk)
    
    if request.method == 'GET':
        serializer = BusSerializer(bus)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BusSerializer(bus, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        bus.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Schedule Recurrence Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_schedule_recurrences(request):
    """List or create schedule recurrences."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        recurrences = ScheduleRecurrence.objects.select_related('route', 'bus').all()
        serializer = ScheduleRecurrenceSerializer(recurrences, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ScheduleRecurrenceSerializer(data=request.data)
        if serializer.is_valid():
            recurrence = serializer.save()
            # Generate occurrences for next 60 days
            from datetime import timedelta
            today = date.today()
            for i in range(60):
                schedule_date = today + timedelta(days=i)
                # For weekly recurrences, only create on the same day of week
                # For daily, create all days
                if recurrence.recurrence_type == 'daily':
                    ScheduleOccurrence.objects.get_or_create(
                        recurrence=recurrence,
                        date=schedule_date,
                        defaults={
                            'departure_time': recurrence.departure_time,
                            'arrival_time': recurrence.arrival_time,
                            'status': 'scheduled'
                        }
                    )
                elif recurrence.recurrence_type == 'weekly':
                    # For weekly, create occurrences every 7 days starting from today
                    # This is a simplified approach - in production you might track specific weekdays
                    if i % 7 == 0:
                        ScheduleOccurrence.objects.get_or_create(
                            recurrence=recurrence,
                            date=schedule_date,
                            defaults={
                                'departure_time': recurrence.departure_time,
                                'arrival_time': recurrence.arrival_time,
                                'status': 'scheduled'
                            }
                        )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'PUT', 'DELETE'])
def admin_schedule_recurrence_detail(request, pk):
    """Get, update, or delete a schedule recurrence."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    recurrence = get_object_or_404(ScheduleRecurrence, pk=pk)
    
    if request.method == 'GET':
        serializer = ScheduleRecurrenceSerializer(recurrence)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ScheduleRecurrenceSerializer(recurrence, data=request.data, partial=True)
        if serializer.is_valid():
            updated_recurrence = serializer.save()
            
            # Update existing occurrences with new times if they changed
            if 'departure_time' in request.data or 'arrival_time' in request.data:
                ScheduleOccurrence.objects.filter(
                    recurrence=updated_recurrence,
                    status='scheduled'
                ).update(
                    departure_time=updated_recurrence.departure_time,
                    arrival_time=updated_recurrence.arrival_time
                )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Delete all associated occurrences first
        ScheduleOccurrence.objects.filter(recurrence=recurrence).delete()
        recurrence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Booking Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET'])
def admin_bookings(request):
    """List all bookings."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    bookings = Booking.objects.select_related(
        'schedule_occurrence__recurrence__route',
        'schedule_occurrence__recurrence__bus'
    ).all().order_by('-created_at')
    
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


# Operator Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_operators(request):
    """List or create operators."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        operators = OperatorUser.objects.select_related('user').all()
        data = []
        for op in operators:
            data.append({
                'id': op.id,
                'username': op.user.username,
                'full_name': op.full_name,
                'phone_number': op.phone_number,
                'email': op.email,
                'is_active': op.is_active,
            })
        return Response(data)
    
    elif request.method == 'POST':
        from accounts.models import User
        username = request.data.get('username')
        password = request.data.get('password')
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or ''
        )
        
        operator = OperatorUser.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            is_active=True
        )
        
        return Response({
            'id': operator.id,
            'username': user.username,
            'full_name': operator.full_name,
            'phone_number': operator.phone_number,
            'email': operator.email,
        }, status=status.HTTP_201_CREATED)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['DELETE'])
def admin_operator_detail(request, pk):
    """Delete an operator."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    operator = get_object_or_404(OperatorUser, pk=pk)
    # Delete the associated User first (this will cascade delete the OperatorUser due to CASCADE)
    user = operator.user
    user.delete()  # This deletes the User, which cascades to delete the OperatorUser
    return Response(status=status.HTTP_204_NO_CONTENT)


# Operator Assignment Management
@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['GET', 'POST'])
def admin_operator_assignments(request):
    """List or create operator assignments."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        assignments = OperatorAssignment.objects.select_related('operator', 'route').all()
        data = []
        for assignment in assignments:
            data.append({
                'id': assignment.id,
                'operator_id': assignment.operator.id,
                'operator_name': assignment.operator.full_name,
                'route_id': assignment.route.id,
                'route_name': assignment.route.name,
                'is_active': assignment.is_active,
            })
        return Response(data)
    
    elif request.method == 'POST':
        operator_id = request.data.get('operator_id')
        route_id = request.data.get('route_id')
        
        operator = get_object_or_404(OperatorUser, pk=operator_id)
        route = get_object_or_404(Route, pk=route_id)
        
        assignment, created = OperatorAssignment.objects.get_or_create(
            operator=operator,
            route=route,
            defaults={'is_active': True}
        )
        
        if not created:
            assignment.is_active = True
            assignment.save()
        
        return Response({
            'id': assignment.id,
            'operator_id': operator.id,
            'route_id': route.id,
        }, status=status.HTTP_201_CREATED)


@csrf_exempt
@authentication_classes([SessionAuthentication])
@api_view(['DELETE'])
def admin_operator_assignment_detail(request, pk):
    """Delete an operator assignment."""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    assignment = get_object_or_404(OperatorAssignment, pk=pk)
    assignment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

