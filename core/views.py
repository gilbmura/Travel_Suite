"""
Views for Travel Suite - Django REST Framework ViewSets
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import (
    User, AdminProfile, OperatorProfile, Customer, Route, Vehicle, 
    Seat, Event, Booking, Ticket, Payment, Transaction
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    AdminProfileSerializer, OperatorProfileSerializer, CustomerSerializer,
    RouteSerializer, VehicleSerializer, SeatSerializer, EventSerializer,
    BookingSerializer, TicketSerializer, PaymentSerializer, TransactionSerializer
)
from .utils import validate_ticket, check_seat_availability


class UserRegistrationViewSet(viewsets.ViewSet):
    """ViewSet for user registration."""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


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


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet for Vehicle model - Full CRUD operations."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        """Get all seats for a vehicle."""
        vehicle = self.get_object()
        seats = vehicle.seats.all()
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)


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
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking."""
        booking = self.get_object()
        booking.status = 'Confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        booking.status = 'Cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
