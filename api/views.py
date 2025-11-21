from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Prefetch
from datetime import date, timedelta

from routes.models import District, Route
from bookings.models import ScheduleOccurrence, Booking, ScheduleRecurrence
from payments.models import PaymentTransaction, Refund
from payments.mtn_adapter import MTNAdapter
from payments.airtel_adapter import AirtelAdapter
from notifications.email import send_notification_async
from operators.models import OperatorUser, OperatorAssignment

from .serializers import (
    DistrictSerializer, RouteSerializer, ScheduleOccurrenceSerializer,
    BookingSerializer, BookingCreateSerializer, BookingStatusSerializer,
    OperatorUserSerializer, OperatorAssignmentSerializer
)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for districts."""
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for routes."""
    queryset = Route.objects.select_related('origin', 'destination').filter(is_active=True)
    serializer_class = RouteSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        from_location = self.request.query_params.get('from', None)
        if from_location:
            queryset = queryset.filter(origin__name__icontains=from_location)
        return queryset


class ScheduleOccurrenceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for schedule occurrences."""
    queryset = ScheduleOccurrence.objects.select_related(
        'recurrence__route__origin',
        'recurrence__route__destination',
        'recurrence__bus'
    )
    serializer_class = ScheduleOccurrenceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # For list view, only show scheduled occurrences that haven't departed yet
        # For retrieve (detail) view, allow any status for validation
        if self.action == 'retrieve':
            queryset = ScheduleOccurrence.objects.select_related(
                'recurrence__route__origin',
                'recurrence__route__destination',
                'recurrence__bus'
            )
        else:
            now = timezone.now()
            today = date.today()
            
            queryset = ScheduleOccurrence.objects.select_related(
                'recurrence__route__origin',
                'recurrence__route__destination',
                'recurrence__bus'
            ).filter(
                status='scheduled'
            ).exclude(
                # Exclude schedules where departure time has passed
                Q(date__lt=today) |  # Past dates
                Q(
                    date=today,
                    departure_time__lt=now.time()
                )  # Today but departure time has passed
            )
        
        route_id = self.request.query_params.get('route_id', None)
        schedule_date = self.request.query_params.get('date', None)
        
        if route_id:
            queryset = queryset.filter(recurrence__route_id=route_id)
        
        if schedule_date:
            try:
                date_obj = date.fromisoformat(schedule_date)
                queryset = queryset.filter(date=date_obj)
                # For specific date, also filter out past times if it's today
                if date_obj == date.today():
                    now = timezone.now()
                    queryset = queryset.exclude(departure_time__lt=now.time())
            except ValueError:
                pass
        else:
            # Default to today and future dates (only for list view)
            if self.action != 'retrieve':
                queryset = queryset.filter(date__gte=date.today())
        
        return queryset.order_by('date', 'departure_time')


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for bookings."""
    queryset = Booking.objects.select_related(
        'schedule_occurrence__recurrence__route',
        'schedule_occurrence__recurrence__bus'
    ).all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'status':
            return BookingStatusSerializer
        return BookingSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new booking with payment processing."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        schedule_occurrence_id = serializer.validated_data['schedule_occurrence_id']
        
        # Lock the schedule occurrence to prevent overbooking
        schedule_occurrence = ScheduleOccurrence.objects.select_for_update().get(
            id=schedule_occurrence_id,
            status='scheduled'
        )
        
        # Check if departure time has passed
        from datetime import datetime
        now = timezone.now()
        departure_datetime = timezone.make_aware(
            datetime.combine(schedule_occurrence.date, schedule_occurrence.departure_time)
        )
        if departure_datetime <= now:
            return Response(
                {'error': 'Cannot book for a schedule that has already departed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check availability
        if schedule_occurrence.remaining_seats <= 0:
            return Response(
                {'error': 'No seats available for this schedule'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create booking
        booking = Booking.objects.create(
            passenger_name=serializer.validated_data['passenger_name'],
            phone_number=serializer.validated_data['phone_number'],
            email=serializer.validated_data.get('email'),
            schedule_occurrence=schedule_occurrence,
            payment_method=serializer.validated_data['payment_method'],
            status='pending'
        )
        
        # Process payment
        payment_method = serializer.validated_data['payment_method']
        phone_number = serializer.validated_data['phone_number']
        amount = float(schedule_occurrence.recurrence.route.fare)  # Get fare from route
        
        if payment_method == 'mtn':
            payment_result = MTNAdapter.create_payment(
                phone_number=phone_number,
                amount=amount,
                idempotency_key=str(booking.id)
            )
        elif payment_method == 'airtel':
            payment_result = AirtelAdapter.create_payment(
                phone_number=phone_number,
                amount=amount,
                idempotency_key=str(booking.id)
            )
        elif payment_method == 'cash':
            payment_result = {
                'success': True,
                'transaction_id': f'CASH_{booking.id}',
                'status': 'completed'
            }
        else:
            return Response(
                {'error': 'Invalid payment method'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment transaction
        payment_transaction = PaymentTransaction.objects.create(
            provider=payment_method,
            provider_transaction_id=payment_result.get('transaction_id'),
            amount=amount,
            status='pending',
            response_raw=payment_result.get('response_raw', {}),
            idempotency_key=str(booking.id),
            booking=booking
        )
        
        # Verify payment (for mobile money)
        if payment_method in ['mtn', 'airtel']:
            adapter = MTNAdapter if payment_method == 'mtn' else AirtelAdapter
            verify_result = adapter.verify_payment(payment_result['transaction_id'])
            if verify_result['success'] and verify_result['status'] == 'completed':
                payment_transaction.status = 'completed'
                payment_transaction.save()
                booking.status = 'confirmed'
                booking.save()
                
                # Send notifications
                send_notification_async(booking, schedule_occurrence)
            else:
                payment_transaction.status = 'failed'
                payment_transaction.save()
                return Response(
                    {'error': 'Payment verification failed'},
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
        else:  # Cash
            payment_transaction.status = 'completed'
            payment_transaction.save()
            booking.status = 'confirmed'
            booking.save()
            
            # Send notifications
            send_notification_async(booking, schedule_occurrence)
        
        response_serializer = BookingSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking and process refund if eligible."""
        booking = self.get_object()
        
        if not booking.can_cancel():
            return Response(
                {'error': 'Booking cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check refund eligibility
        can_refund = booking.can_refund()
        
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        refund_id = None
        if can_refund and booking.payment_method != 'cash':
            # Process automatic refund
            try:
                payment_transaction = booking.payment_transaction
                adapter = MTNAdapter if booking.payment_method == 'mtn' else AirtelAdapter
                
                refund_result = adapter.refund_payment(
                    transaction_id=payment_transaction.provider_transaction_id,
                    amount=payment_transaction.amount
                )
                
                if refund_result['success']:
                    refund_id = refund_result['refund_id']
                    booking.refund_id = refund_id
                    booking.save()
                    
                    # Create refund record
                    Refund.objects.create(
                        payment_transaction=payment_transaction,
                        amount=payment_transaction.amount,
                        status='completed',
                        provider_refund_id=refund_id,
                        response_raw=refund_result.get('response_raw', {})
                    )
                    
                    payment_transaction.status = 'refunded'
                    payment_transaction.save()
            except Exception as e:
                # Log error but don't fail cancellation
                pass
        
        return Response({
            'message': 'Booking cancelled successfully',
            'refund_processed': can_refund and booking.payment_method != 'cash',
            'refund_id': refund_id
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get booking status."""
        booking = self.get_object()
        serializer = BookingStatusSerializer(booking)
        return Response(serializer.data)


class OperatorBookingViewSet(viewsets.ModelViewSet):
    """ViewSet for operator bookings (cash bookings)."""
    queryset = Booking.objects.select_related(
        'schedule_occurrence__recurrence__route',
        'schedule_occurrence__recurrence__bus'
    ).all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Filter bookings by operator's assigned routes."""
        if not hasattr(self.request.user, 'operator_profile'):
            return Booking.objects.none()
        
        operator = self.request.user.operator_profile
        assigned_routes = OperatorAssignment.objects.filter(
            operator=operator,
            is_active=True
        ).values_list('route_id', flat=True)
        
        return self.queryset.filter(
            schedule_occurrence__recurrence__route_id__in=assigned_routes
        )
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a cash booking on behalf of customer."""
        if not hasattr(request.user, 'operator_profile'):
            return Response(
                {'error': 'User is not an operator'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        operator = request.user.operator_profile
        
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        schedule_occurrence_id = serializer.validated_data['schedule_occurrence_id']
        
        # Lock the schedule occurrence
        schedule_occurrence = ScheduleOccurrence.objects.select_for_update().get(
            id=schedule_occurrence_id,
            status='scheduled'
        )
        
        # Check if departure time has passed
        from datetime import datetime
        now = timezone.now()
        departure_datetime = timezone.make_aware(
            datetime.combine(schedule_occurrence.date, schedule_occurrence.departure_time)
        )
        if departure_datetime <= now:
            return Response(
                {'error': 'Cannot book for a schedule that has already departed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify operator has access to this route
        if not OperatorAssignment.objects.filter(
            operator=operator,
            route=schedule_occurrence.recurrence.route,
            is_active=True
        ).exists():
            return Response(
                {'error': 'Operator not assigned to this route'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check availability
        if schedule_occurrence.remaining_seats <= 0:
            return Response(
                {'error': 'No seats available for this schedule'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create booking with cash payment
        booking = Booking.objects.create(
            passenger_name=serializer.validated_data['passenger_name'],
            phone_number=serializer.validated_data['phone_number'],
            email=serializer.validated_data.get('email'),
            schedule_occurrence=schedule_occurrence,
            payment_method='cash',
            status='confirmed',
            operator=operator
        )
        
        # Create payment transaction
        amount = float(schedule_occurrence.recurrence.route.fare)  # Get fare from route
        PaymentTransaction.objects.create(
            provider='cash',
            provider_transaction_id=f'CASH_{booking.id}',
            amount=amount,
            status='completed',
            booking=booking
        )
        
        # Send notifications
        send_notification_async(booking, schedule_occurrence)
        
        response_serializer = BookingSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def route_bookings(self, request):
        """Get bookings for a specific route."""
        route_id = request.query_params.get('route_id')
        if not route_id:
            return Response(
                {'error': 'route_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not hasattr(request.user, 'operator_profile'):
            return Response(
                {'error': 'User is not an operator'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        operator = request.user.operator_profile
        
        # Verify operator has access
        if not OperatorAssignment.objects.filter(
            operator=operator,
            route_id=route_id,
            is_active=True
        ).exists():
            return Response(
                {'error': 'Operator not assigned to this route'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        bookings = self.get_queryset().filter(
            schedule_occurrence__recurrence__route_id=route_id
        )
        
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assigned_routes(self, request):
        """Get routes assigned to the operator."""
        if not hasattr(request.user, 'operator_profile'):
            return Response(
                {'error': 'User is not an operator'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        operator = request.user.operator_profile
        assignments = OperatorAssignment.objects.filter(
            operator=operator,
            is_active=True
        ).select_related('route')
        
        routes = [assignment.route for assignment in assignments]
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_schedule_departed(request, schedule_id):
    """Mark a schedule occurrence as departed."""
    if not hasattr(request.user, 'operator_profile'):
        return Response(
            {'error': 'User is not an operator'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    operator = request.user.operator_profile
    schedule_occurrence = get_object_or_404(ScheduleOccurrence, id=schedule_id)
    
    # Verify operator has access
    if not OperatorAssignment.objects.filter(
        operator=operator,
        route=schedule_occurrence.recurrence.route,
        is_active=True
    ).exists():
        return Response(
            {'error': 'Operator not assigned to this route'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    schedule_occurrence.status = 'departed'
    schedule_occurrence.save()
    
    return Response({
        'message': 'Schedule marked as departed',
        'schedule_id': schedule_id
    })


# Frontend views
def index_view(request):
    """Landing page."""
    return render(request, 'index.html')


def routes_view(request):
    """Routes listing page."""
    return render(request, 'routes.html')


def schedules_view(request):
    """Schedules listing page."""
    return render(request, 'schedules.html')


def booking_view(request):
    """Booking form page."""
    return render(request, 'booking.html')


def operator_login_view(request):
    """Operator login page."""
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is an operator
            if hasattr(user, 'operator_profile'):
                login(request, user)
                next_url = request.POST.get('next', '/operator/dashboard/')
                from django.shortcuts import redirect
                return redirect(next_url)
            else:
                return render(request, 'operator/login.html', {
                    'error': 'User is not an operator'
                })
        else:
            return render(request, 'operator/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'operator/login.html')


def operator_logout_view(request):
    """Operator logout view."""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    
    logout(request)
    return redirect('operator-login')


def operator_dashboard_view(request):
    """Operator dashboard."""
    from django.contrib.auth.decorators import login_required
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    
    if not request.user.is_authenticated:
        return redirect('operator-login')
    
    if not hasattr(request.user, 'operator_profile'):
        logout(request)
        return redirect('operator-login')
    
    return render(request, 'operator/dashboard.html')


def admin_login_view(request):
    """Admin login page."""
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        from django.shortcuts import redirect
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is staff/superuser
            if user.is_staff or user.is_superuser:
                login(request, user)
                next_url = request.POST.get('next', '/admin/dashboard/')
                return redirect(next_url)
            else:
                return render(request, 'admin/login.html', {
                    'error': 'User does not have admin privileges'
                })
        else:
            return render(request, 'admin/login.html', {
                'error': 'Invalid username or password'
            })
    
    return render(request, 'admin/login.html')


def admin_logout_view(request):
    """Admin logout view."""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    
    logout(request)
    return redirect('admin-login')


def admin_dashboard_view(request):
    """Admin dashboard."""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    
    if not request.user.is_authenticated:
        return redirect('admin-login')
    
    if not (request.user.is_staff or request.user.is_superuser):
        logout(request)
        return redirect('admin-login')
    
    # Import here to avoid circular import
    from . import admin_views
    return admin_views.admin_dashboard_view(request)

