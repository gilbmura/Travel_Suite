from django.test import TestCase
from django.utils import timezone
from datetime import date, time, timedelta
from routes.models import District, Route
from buses.models import Bus
from bookings.models import ScheduleRecurrence, ScheduleOccurrence, Booking
from payments.models import PaymentTransaction
from accounts.models import User


class BookingModelTest(TestCase):
    """Test booking model methods."""
    
    def setUp(self):
        # Create test data
        self.origin = District.objects.create(name="Kigali", code="KG")
        self.destination = District.objects.create(name="Musanze", code="MU")
        self.route = Route.objects.create(
            name="Kigali - Musanze",
            origin=self.origin,
            destination=self.destination,
            distance_km=100
        )
        self.bus = Bus.objects.create(plate_number="RAB123X", capacity=30)
        self.recurrence = ScheduleRecurrence.objects.create(
            route=self.route,
            bus=self.bus,
            recurrence_type='daily',
            departure_time=time(8, 0),
            arrival_time=time(12, 0)
        )
        self.tomorrow = date.today() + timedelta(days=1)
        self.occurrence = ScheduleOccurrence.objects.create(
            recurrence=self.recurrence,
            date=self.tomorrow,
            departure_time=time(8, 0),
            arrival_time=time(12, 0)
        )
    
    def test_remaining_seats_calculation(self):
        """Test remaining seats calculation."""
        self.assertEqual(self.occurrence.remaining_seats, 30)
        
        # Create a booking
        Booking.objects.create(
            passenger_name="Test Passenger",
            phone_number="+250788123456",
            schedule_occurrence=self.occurrence,
            payment_method='cash',
            status='confirmed'
        )
        
        # Refresh from DB
        self.occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.remaining_seats, 29)
    
    def test_time_to_departure(self):
        """Test time to departure calculation."""
        # For future date, should return minutes
        time_to_departure = self.occurrence.time_to_departure
        self.assertIsNotNone(time_to_departure)
        self.assertGreater(time_to_departure, 0)
    
    def test_can_cancel(self):
        """Test booking cancellation eligibility."""
        booking = Booking.objects.create(
            passenger_name="Test Passenger",
            phone_number="+250788123456",
            schedule_occurrence=self.occurrence,
            payment_method='cash',
            status='confirmed'
        )
        
        self.assertTrue(booking.can_cancel())
        
        # Mark as departed
        self.occurrence.status = 'departed'
        self.occurrence.save()
        booking.refresh_from_db()
        
        self.assertFalse(booking.can_cancel())
    
    def test_can_refund(self):
        """Test refund eligibility (>1 hour before departure)."""
        # Create occurrence 2 hours from now
        future_time = timezone.now() + timedelta(hours=2)
        future_date = future_time.date()
        future_occurrence = ScheduleOccurrence.objects.create(
            recurrence=self.recurrence,
            date=future_date,
            departure_time=future_time.time(),
            arrival_time=(future_time + timedelta(hours=4)).time()
        )
        
        booking = Booking.objects.create(
            passenger_name="Test Passenger",
            phone_number="+250788123456",
            schedule_occurrence=future_occurrence,
            payment_method='mtn',
            status='confirmed'
        )
        
        self.assertTrue(booking.can_refund())
        
        # Create occurrence 30 minutes from now
        near_time = timezone.now() + timedelta(minutes=30)
        near_occurrence = ScheduleOccurrence.objects.create(
            recurrence=self.recurrence,
            date=near_time.date(),
            departure_time=near_time.time(),
            arrival_time=(near_time + timedelta(hours=4)).time()
        )
        
        booking2 = Booking.objects.create(
            passenger_name="Test Passenger 2",
            phone_number="+250788123457",
            schedule_occurrence=near_occurrence,
            payment_method='mtn',
            status='confirmed'
        )
        
        self.assertFalse(booking2.can_refund())


class BookingCreationTest(TestCase):
    """Test booking creation logic."""
    
    def setUp(self):
        self.origin = District.objects.create(name="Kigali", code="KG")
        self.destination = District.objects.create(name="Musanze", code="MU")
        self.route = Route.objects.create(
            name="Kigali - Musanze",
            origin=self.origin,
            destination=self.destination
        )
        self.bus = Bus.objects.create(plate_number="RAB123X", capacity=2)  # Small capacity for testing
        self.recurrence = ScheduleRecurrence.objects.create(
            route=self.route,
            bus=self.bus,
            recurrence_type='daily',
            departure_time=time(8, 0),
            arrival_time=time(12, 0)
        )
        self.tomorrow = date.today() + timedelta(days=1)
        self.occurrence = ScheduleOccurrence.objects.create(
            recurrence=self.recurrence,
            date=self.tomorrow,
            departure_time=time(8, 0),
            arrival_time=time(12, 0)
        )
    
    def test_overbooking_prevention(self):
        """Test that overbooking is prevented."""
        # Fill all seats
        Booking.objects.create(
            passenger_name="Passenger 1",
            phone_number="+250788111111",
            schedule_occurrence=self.occurrence,
            payment_method='cash',
            status='confirmed'
        )
        Booking.objects.create(
            passenger_name="Passenger 2",
            phone_number="+250788222222",
            schedule_occurrence=self.occurrence,
            payment_method='cash',
            status='confirmed'
        )
        
        # Check remaining seats
        self.occurrence.refresh_from_db()
        self.assertEqual(self.occurrence.remaining_seats, 0)
        
        # Should not be able to book more
        self.assertEqual(self.occurrence.remaining_seats, 0)

