"""
Views for Travel Suite - Django REST Framework ViewSets
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from datetime import datetime

from .models import (
    User, AdminProfile, OperatorProfile, OperatorAssignment,
    Customer, Route, Vehicle, Seat, Event, Booking, Ticket,
    Payment, Transaction
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    AdminProfileSerializer, OperatorProfileSerializer, CustomerSerializer,
    RouteSerializer, VehicleSerializer, SeatSerializer, EventSerializer,
    BookingSerializer, PublicBookingSerializer, TicketSerializer,
    PaymentSerializer, TransactionSerializer
)
from .utils import (
    validate_ticket,
    check_seat_availability,
    operator_route_ids,
    get_next_booking_id,
)
from .permissions import IsApprovedOperator
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class UserRegistrationViewSet(viewsets.ViewSet):
    """ViewSet for user registration."""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # If operator, don't return tokens (they need approval first)
            if user.is_operator:
                return Response({
                    'message': 'Registration successful! Your account is pending admin approval. You will be able to log in once an admin approves your account.',
                    'user': UserSerializer(user).data,
                    'pending_approval': True
                }, status=status.HTTP_201_CREATED)
            
            # For admins and regular users, return tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login endpoint."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model - CRUD operations."""
    queryset = User.objects.all().prefetch_related('operator_profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_active(self, request, pk=None):
        """Allow admin users to enable/disable a user's active state (grant/revoke access).

        Expected payload: { "is_active": true|false }
        """
        # simple permission check: only admins or superusers can toggle access
        user = self.get_object()
        requester = request.user
        if not (getattr(requester, 'is_admin', False) or requester.is_superuser or requester.is_staff):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        is_active = request.data.get('is_active')
        if is_active is None:
            return Response({'detail': 'is_active field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = bool(is_active)
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def pending_operators(self, request):
        """Get list of operators pending approval (admin only)."""
        requester = request.user
        if not (getattr(requester, 'is_admin', False) or requester.is_superuser or requester.is_staff):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        pending_operators = OperatorProfile.objects.filter(is_approved=False).select_related('user')
        serializer = OperatorProfileSerializer(pending_operators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def approved_operators(self, request):
        """Get list of approved operators (admin only)."""
        requester = request.user
        if not (getattr(requester, 'is_admin', False) or requester.is_superuser or requester.is_staff):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        approved_operators = OperatorProfile.objects.filter(is_approved=True).select_related('user')
        serializer = OperatorProfileSerializer(approved_operators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve_operator(self, request, pk=None):
        """Approve an operator account (admin only).
        
        Expected payload: { "is_approved": true|false }
        """
        requester = request.user
        if not (getattr(requester, 'is_admin', False) or requester.is_superuser or requester.is_staff):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        if not user.is_operator:
            return Response({'detail': 'User is not an operator.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            operator_profile = user.operator_profile
        except OperatorProfile.DoesNotExist:
            return Response({'detail': 'Operator profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        is_approved = request.data.get('is_approved')
        if is_approved is None:
            return Response({'detail': 'is_approved field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        operator_profile.is_approved = bool(is_approved)
        operator_profile.save()
        
        # Also activate the user account when approved
        if is_approved:
            user.is_active = True
            user.is_approved = True
            user.save(update_fields=['is_active', 'is_approved'])
        else:
            # If unapproved, deactivate the account
            user.is_active = False
            user.is_approved = False
            user.save(update_fields=['is_active', 'is_approved'])
        
        serializer = OperatorProfileSerializer(operator_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model - Full CRUD operations."""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter customers if needed."""
        return super().get_queryset()


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet for Route model - Full CRUD operations."""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def available_seats(self, request, pk=None):
        """Get available seats for a specific route."""
        route = self.get_object()
        vehicles = Vehicle.objects.filter(route=route)
        available = 0
        for vehicle in vehicles:
            available += check_seat_availability(vehicle, None)
        return Response({'route_id': pk, 'available_seats': available})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsApprovedOperator], url_path='operator')
    def operator_routes(self, request):
        """List routes assigned to the current operator."""
        route_ids = operator_route_ids(request.user)
        queryset = self.get_queryset().filter(id__in=route_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='filters')
    def route_filters(self, request):
        """Public endpoint to get unique origins and destinations for dropdowns."""
        origins = sorted(Route.objects.values_list('origin', flat=True).distinct().exclude(origin__isnull=True).exclude(origin=''))
        destinations = sorted(Route.objects.values_list('destination', flat=True).distinct().exclude(destination__isnull=True).exclude(destination=''))
        # Normalize to uppercase for consistency and case-insensitive matching
        origins = [o.upper() if o else o for o in origins]
        destinations = [d.upper() if d else d for d in destinations]
        return Response({
            'origins': list(origins),
            'destinations': list(destinations)
        })


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model - Full CRUD operations."""
    queryset = Vehicle.objects.select_related('route').all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """Get all seats for a vehicle."""
        vehicle = self.get_object()
        seats = vehicle.seats.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsApprovedOperator], url_path='operator')
    def operator_vehicles(self, request):
        """List vehicles assigned to the operator."""
        route_ids = operator_route_ids(request.user)
        queryset = self.get_queryset().filter(route_id__in=route_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='search')
    def search(self, request):
        """Public search endpoint for available vehicles."""
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        date_str = request.query_params.get('date')

        if not (origin and destination and date_str):
            return Response(
                {'detail': 'origin, destination and date query parameters are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            travel_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        routes = Route.objects.filter(
            origin__iexact=origin,
            destination__iexact=destination
        )
        vehicles = self.get_queryset().filter(route__in=routes, status='Available')

        data = []
        for vehicle in vehicles:
            available = check_seat_availability(vehicle, travel_date)
            data.append({
                'vehicle_id': vehicle.id,
                'license_plate': vehicle.license_plate,
                'route_id': vehicle.route_id,
                'origin': vehicle.route.origin if vehicle.route else None,
                'destination': vehicle.route.destination if vehicle.route else None,
                'fare': str(vehicle.route.fare) if vehicle.route else None,
                'departure_time': vehicle.route.departure_time if vehicle.route else None,
                'available_seats': available,
                'capacity': vehicle.capacity,
            })
        return Response(data)


class SeatViewSet(viewsets.ModelViewSet):
    """ViewSet for Seat model - Full CRUD operations."""
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        """Book a seat."""
        seat = self.get_object()
        if seat.is_booked:
            return Response(
                {'error': 'Seat is already booked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        seat.is_booked = True
        seat.save()
        serializer = self.get_serializer(seat)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unbook(self, request, pk=None):
        """Unbook a seat."""
        seat = self.get_object()
        seat.is_booked = False
        seat.booking = None
        seat.save()
        serializer = self.get_serializer(seat)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event model - Full CRUD operations."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model - Full CRUD operations."""
    queryset = Booking.objects.select_related('route', 'vehicle', 'customer').all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['public_create', 'client_cancel', 'client_status']:
            return [AllowAny()]
        if self.action in ['operator_bookings', 'operator_cancel']:
            return [IsAuthenticated(), IsApprovedOperator()]
        if self.action in ['admin_dashboard']:
            return [IsAuthenticated(), IsAdminUser()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Save booking via admin/internal flows."""
        booking = serializer.save()
        self._notify_new_booking(booking)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking (admin only)."""
        booking = self.get_object()
        booking.status = 'CONFIRMED'
        booking.save(update_fields=['status'])
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking (admin override)."""
        booking = self.get_object()
        self._cancel_booking(booking, reason='admin')
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='public', permission_classes=[AllowAny])
    def public_create(self, request):
        """Allow clients to create bookings without authentication."""
        serializer = PublicBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking, payment = self._create_public_booking(serializer.validated_data)
        return Response({
            'booking_id': booking.booking_id,
            'status': booking.status,
            'payment_status': payment.status,
            'travel_date': booking.travel_date,
            'route': booking.route_id,
            'vehicle': booking.vehicle_id,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='client-cancel', permission_classes=[AllowAny])
    def client_cancel(self, request):
        """Allow clients to cancel a booking if more than 2 hours remain."""
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({'detail': 'booking_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not self._can_client_cancel(booking):
            return Response({'detail': 'Cancellations must be requested more than 2 hours before departure.'},
                            status=status.HTTP_400_BAD_REQUEST)

        self._cancel_booking(booking, reason='client')
        return Response({'detail': 'Booking cancelled successfully.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='client-status', permission_classes=[AllowAny])
    def client_status(self, request):
        """Allow clients to check booking status."""
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response({'detail': 'booking_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='operator', permission_classes=[IsAuthenticated, IsApprovedOperator])
    def operator_bookings(self, request):
        """List bookings for routes assigned to the operator."""
        route_ids = operator_route_ids(request.user)
        queryset = self.get_queryset().filter(route_id__in=route_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='operator-cancel', permission_classes=[IsAuthenticated, IsApprovedOperator])
    def operator_cancel(self, request, pk=None):
        """Allow operators to cancel bookings for their routes."""
        booking = self.get_object()
        route_ids = operator_route_ids(request.user)
        if booking.route_id not in route_ids:
            return Response({'detail': 'You are not authorized to manage this booking.'},
                            status=status.HTTP_403_FORBIDDEN)
        self._cancel_booking(booking, reason='operator')
        return Response({'detail': 'Booking cancelled.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='admin/dashboard', permission_classes=[IsAuthenticated, IsAdminUser])
    def admin_dashboard(self, request):
        """Aggregate stats for the admin dashboard."""
        return Response({
            'total_routes': Route.objects.count(),
            'total_vehicles': Vehicle.objects.count(),
            'active_bookings': Booking.objects.filter(status='CONFIRMED').count(),
            'pending_operators': OperatorProfile.objects.filter(is_approved=False).count(),
        })

    def _create_public_booking(self, data):
        vehicle = data['vehicle']
        travel_date = data['travel_date']
        seats = data.get('seats_booked', 1)
        customer_name = data['customer_name']
        payment_method = data['payment_method']

        with transaction.atomic():
            available = check_seat_availability(vehicle, travel_date)
            if seats > available:
                raise ValidationError({'seats_booked': f'Only {available} seats available for this vehicle on {travel_date}.'})

            route = vehicle.route
            fare = Decimal(route.fare) if route and route.fare is not None else Decimal('0.00')
            amount = fare * seats
            booking = Booking.objects.create(
                booking_id=get_next_booking_id(),
                customer_name=customer_name,
                vehicle=vehicle,
                route=route,
                seats_booked=seats,
                amount=amount,
                travel_date=travel_date,
                status='CONFIRMED'
            )
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_method=payment_method,
                status='Completed'
            )
        self._notify_new_booking(booking)
        return booking, payment

    def _can_client_cancel(self, booking):
        if booking.status == 'CANCELLED':
            return False
        if not booking.travel_date or not booking.route:
            return False
        departure_time = booking.route.departure_time
        if not departure_time:
            return True
        departure_dt = datetime.combine(booking.travel_date, departure_time)
        departure_dt = timezone.make_aware(departure_dt, timezone.get_current_timezone())
        return (departure_dt - timezone.now()).total_seconds() > 7200

    def _cancel_booking(self, booking, reason):
        if booking.status == 'CANCELLED':
            return booking

        booking.status = 'CANCELLED'
        booking.save(update_fields=['status'])
        Payment.objects.filter(booking=booking).update(status='Completed')
        return booking

    def _notify_new_booking(self, booking):
        """Send non-blocking notification via channels."""
        try:
            channel_layer = get_channel_layer()
            payload = {
                'id': booking.id,
                'booking_id': booking.booking_id,
                'customer': booking.customer_name or getattr(getattr(booking, 'customer', None), 'name', ''),
                'route': str(booking.route) if booking.route else None,
                'vehicle': booking.vehicle.license_plate if booking.vehicle else None,
                'date': booking.travel_date.isoformat() if booking.travel_date else None,
                'status': booking.status,
            }
            async_to_sync(channel_layer.group_send)(
                'operators',
                {
                    'type': 'new_booking',
                    'booking': payload
                }
            )
        except Exception as exc:
            print('Operator notify error:', exc)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket model - Full CRUD operations."""
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def validate_ticket(self, request):
        """Validate a ticket by QR code."""
        qr_code = request.data.get('qr_code')
        result = validate_ticket(qr_code)
        if result['status'] == 'success':
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model - Full CRUD operations."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process a payment."""
        payment = self.get_object()
        payment.status = 'Completed'
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model - Full CRUD operations."""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
