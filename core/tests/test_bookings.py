from datetime import timedelta, time
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import (
    User,
    OperatorProfile,
    OperatorAssignment,
    Route,
    Vehicle,
    Booking,
)


class BookingWorkflowTests(APITestCase):
    def _create_route(self, origin='Kigali', destination='Musanze', depart_time=time(8, 0), fare='2000.00'):
        return Route.objects.create(
            origin=origin,
            destination=destination,
            departure_time=depart_time,
            fare=Decimal(fare)
        )

    def _create_vehicle(self, route, plate_suffix):
        return Vehicle.objects.create(
            license_plate=f"RAD{plate_suffix}",
            route=route,
            capacity=50,
            status='Available'
        )

    def test_public_booking_respects_capacity(self):
        route = self._create_route()
        vehicle = self._create_vehicle(route, '001')
        Booking.objects.create(
            booking_id='B1000',
            customer_name='Existing',
            vehicle=vehicle,
            route=route,
            seats_booked=50,
            amount=Decimal('100000.00'),
            status='CONFIRMED',
            travel_date=timezone.now().date()
        )

        payload = {
            'customer_name': 'Walk In',
            'vehicle_id': vehicle.id,
            'travel_date': timezone.now().date().isoformat(),
            'seats_booked': 1,
            'payment_method': 'Cash',
            'payment_details': '0780000000'
        }
        response = self.client.post('/api/bookings/public/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('seats_booked', response.json())

    def test_client_cancellation_time_window(self):
        soon_route = self._create_route(
            depart_time=(timezone.now() + timedelta(hours=1)).time()
        )
        vehicle = self._create_vehicle(soon_route, '010')
        booking = Booking.objects.create(
            booking_id='B2000',
            customer_name='Soon Traveler',
            vehicle=vehicle,
            route=soon_route,
            seats_booked=1,
            amount=Decimal('5000.00'),
            status='CONFIRMED',
            travel_date=timezone.now().date()
        )
        resp = self.client.post('/api/bookings/client-cancel/', {'booking_id': booking.booking_id}, format='json')
        self.assertEqual(resp.status_code, 400)

        later_route = self._create_route(
            origin='Kigali',
            destination='Nyagatare',
            depart_time=(timezone.now() + timedelta(hours=5)).time()
        )
        later_vehicle = self._create_vehicle(later_route, '020')
        later_booking = Booking.objects.create(
            booking_id='B2001',
            customer_name='Future Traveler',
            vehicle=later_vehicle,
            route=later_route,
            seats_booked=1,
            amount=Decimal('7000.00'),
            status='CONFIRMED',
            travel_date=(timezone.now() + timedelta(days=1)).date()
        )
        resp2 = self.client.post('/api/bookings/client-cancel/', {'booking_id': later_booking.booking_id}, format='json')
        self.assertEqual(resp2.status_code, 200)
        later_booking.refresh_from_db()
        self.assertEqual(later_booking.status, 'CANCELLED')

    def test_operator_scoped_endpoints(self):
        route_a = self._create_route(origin='Kigali', destination='Huye')
        route_b = self._create_route(origin='Kigali', destination='Rubavu', depart_time=time(10, 0))
        vehicle_a = self._create_vehicle(route_a, '101')
        vehicle_b = self._create_vehicle(route_b, '202')

        booking_assigned = Booking.objects.create(
            booking_id='B3000',
            customer_name='Assigned Rider',
            vehicle=vehicle_a,
            route=route_a,
            seats_booked=2,
            amount=Decimal('15000.00'),
            status='CONFIRMED',
            travel_date=timezone.now().date()
        )
        booking_unassigned = Booking.objects.create(
            booking_id='B3001',
            customer_name='Other Rider',
            vehicle=vehicle_b,
            route=route_b,
            seats_booked=1,
            amount=Decimal('8000.00'),
            status='CONFIRMED',
            travel_date=timezone.now().date()
        )

        operator_user = User.objects.create_user(
            username='operator1',
            password='password123',
            is_operator=True,
            is_active=True,
            is_approved=True
        )
        operator_profile = OperatorProfile.objects.create(
            user=operator_user,
            company_name='Express Co',
            license_number='LIC100',
            is_approved=True
        )
        OperatorAssignment.objects.create(operator=operator_profile, route=route_a)

        self.client.force_authenticate(user=operator_user)

        resp = self.client.get('/api/bookings/operator/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]['booking_id'], booking_assigned.booking_id)

        resp_forbidden = self.client.post(f'/api/bookings/{booking_unassigned.id}/operator-cancel/', format='json')
        self.assertEqual(resp_forbidden.status_code, 403)

        resp_allowed = self.client.post(f'/api/bookings/{booking_assigned.id}/operator-cancel/', format='json')
        self.assertEqual(resp_allowed.status_code, 200)
        booking_assigned.refresh_from_db()
        self.assertEqual(booking_assigned.status, 'CANCELLED')

    def test_operator_login_requires_approval(self):
        user = User.objects.create_user(
            username='pendingop',
            password='password123',
            is_operator=True,
            is_active=True,
            is_approved=False
        )
        OperatorProfile.objects.create(
            user=user,
            company_name='Pending Co',
            license_number='LIC555',
            is_approved=False
        )

        resp = self.client.post('/api/auth/login/', {'username': 'pendingop', 'password': 'password123'}, format='json')
        self.assertEqual(resp.status_code, 400)

        user.is_approved = True
        user.save(update_fields=['is_approved'])
        user.operator_profile.is_approved = True
        user.operator_profile.save(update_fields=['is_approved'])

        resp2 = self.client.post('/api/auth/login/', {'username': 'pendingop', 'password': 'password123'}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('access', resp2.json())

