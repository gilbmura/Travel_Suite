"""
Management command to seed sample data for Travel Suite MVP.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from routes.models import District, Route
from buses.models import Bus
from bookings.models import ScheduleRecurrence, ScheduleOccurrence, Booking
from payments.models import PaymentTransaction
from operators.models import OperatorUser, OperatorAssignment
from accounts.models import User


class Command(BaseCommand):
    help = 'Seeds sample data for Travel Suite MVP'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sample data...')
        
        # Create Districts
        self.stdout.write('Creating districts...')
        kigali = District.objects.get_or_create(name="Kigali", defaults={'code': 'KG'})[0]
        musanze = District.objects.get_or_create(name="Musanze", defaults={'code': 'MU'})[0]
        huye = District.objects.get_or_create(name="Huye", defaults={'code': 'HY'})[0]
        rubavu = District.objects.get_or_create(name="Rubavu", defaults={'code': 'RB'})[0]
        
        # Create Routes
        self.stdout.write('Creating routes...')
        route1 = Route.objects.get_or_create(
            name="Kigali - Musanze",
            defaults={
                'origin': kigali,
                'destination': musanze,
                'distance_km': 100,
                'estimated_duration_minutes': 120
            }
        )[0]
        
        route2 = Route.objects.get_or_create(
            name="Kigali - Huye",
            defaults={
                'origin': kigali,
                'destination': huye,
                'distance_km': 150,
                'estimated_duration_minutes': 180
            }
        )[0]
        
        route3 = Route.objects.get_or_create(
            name="Musanze - Rubavu",
            defaults={
                'origin': musanze,
                'destination': rubavu,
                'distance_km': 50,
                'estimated_duration_minutes': 60
            }
        )[0]
        
        # Create Buses
        self.stdout.write('Creating buses...')
        bus1 = Bus.objects.get_or_create(
            plate_number="RAB123X",
            defaults={
                'capacity': 30,
                'company_name': 'Rwanda Express'
            }
        )[0]
        
        bus2 = Bus.objects.get_or_create(
            plate_number="RAB456Y",
            defaults={
                'capacity': 45,
                'company_name': 'Kigali Transport'
            }
        )[0]
        
        # Create Recurring Schedules
        self.stdout.write('Creating recurring schedules...')
        schedule1 = ScheduleRecurrence.objects.get_or_create(
            route=route1,
            bus=bus1,
            departure_time=time(8, 0),
            defaults={
                'recurrence_type': 'daily',
                'arrival_time': time(10, 0),
                'is_active': True
            }
        )[0]
        
        schedule2 = ScheduleRecurrence.objects.get_or_create(
            route=route1,
            bus=bus1,
            departure_time=time(14, 0),
            defaults={
                'recurrence_type': 'daily',
                'arrival_time': time(16, 0),
                'is_active': True
            }
        )[0]
        
        schedule3 = ScheduleRecurrence.objects.get_or_create(
            route=route2,
            bus=bus2,
            departure_time=time(9, 0),
            defaults={
                'recurrence_type': 'daily',
                'arrival_time': time(12, 0),
                'is_active': True
            }
        )[0]
        
        # Create Schedule Occurrences for next 7 days
        self.stdout.write('Creating schedule occurrences...')
        today = date.today()
        for i in range(7):
            schedule_date = today + timedelta(days=i)
            
            # Route 1 - Morning
            ScheduleOccurrence.objects.get_or_create(
                recurrence=schedule1,
                date=schedule_date,
                defaults={
                    'departure_time': schedule1.departure_time,
                    'arrival_time': schedule1.arrival_time,
                    'status': 'scheduled'
                }
            )
            
            # Route 1 - Afternoon
            ScheduleOccurrence.objects.get_or_create(
                recurrence=schedule2,
                date=schedule_date,
                defaults={
                    'departure_time': schedule2.departure_time,
                    'arrival_time': schedule2.arrival_time,
                    'status': 'scheduled'
                }
            )
            
            # Route 2
            ScheduleOccurrence.objects.get_or_create(
                recurrence=schedule3,
                date=schedule_date,
                defaults={
                    'departure_time': schedule3.departure_time,
                    'arrival_time': schedule3.arrival_time,
                    'status': 'scheduled'
                }
            )
        
        # Create Operators
        self.stdout.write('Creating operators...')
        operator_user1 = User.objects.create_user(
            username='operator1',
            email='operator1@travelsuite.rw',
            password='operator123',
            first_name='John',
            last_name='Doe'
        )
        
        operator1 = OperatorUser.objects.get_or_create(
            user=operator_user1,
            defaults={
                'full_name': 'John Doe',
                'phone_number': '+250788111111',
                'email': 'operator1@travelsuite.rw',
                'is_active': True
            }
        )[0]
        
        operator_user2 = User.objects.create_user(
            username='operator2',
            email='operator2@travelsuite.rw',
            password='operator123',
            first_name='Jane',
            last_name='Smith'
        )
        
        operator2 = OperatorUser.objects.get_or_create(
            user=operator_user2,
            defaults={
                'full_name': 'Jane Smith',
                'phone_number': '+250788222222',
                'email': 'operator2@travelsuite.rw',
                'is_active': True
            }
        )[0]
        
        # Create Operator Assignments
        self.stdout.write('Creating operator assignments...')
        OperatorAssignment.objects.get_or_create(
            operator=operator1,
            route=route1,
            defaults={'is_active': True}
        )
        
        OperatorAssignment.objects.get_or_create(
            operator=operator2,
            route=route2,
            defaults={'is_active': True}
        )
        
        # Create Sample Bookings
        self.stdout.write('Creating sample bookings...')
        tomorrow_occurrence = ScheduleOccurrence.objects.filter(
            recurrence=schedule1,
            date=today + timedelta(days=1)
        ).first()
        
        if tomorrow_occurrence:
            booking1 = Booking.objects.create(
                passenger_name="Alice Mukamana",
                phone_number="+250788123456",
                email="alice@example.com",
                schedule_occurrence=tomorrow_occurrence,
                payment_method='mtn',
                status='confirmed'
            )
            
            PaymentTransaction.objects.create(
                provider='mtn',
                provider_transaction_id=f'MTN_{booking1.id}',
                amount=5000,
                status='completed',
                booking=booking1,
                idempotency_key=str(booking1.id)
            )
            
            booking2 = Booking.objects.create(
                passenger_name="Bob Nkurunziza",
                phone_number="+250788654321",
                schedule_occurrence=tomorrow_occurrence,
                payment_method='airtel',
                status='confirmed'
            )
            
            PaymentTransaction.objects.create(
                provider='airtel',
                provider_transaction_id=f'AIRTEL_{booking2.id}',
                amount=5000,
                status='completed',
                booking=booking2,
                idempotency_key=str(booking2.id)
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded sample data!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - {District.objects.count()} districts')
        self.stdout.write(f'  - {Route.objects.count()} routes')
        self.stdout.write(f'  - {Bus.objects.count()} buses')
        self.stdout.write(f'  - {ScheduleRecurrence.objects.count()} recurring schedules')
        self.stdout.write(f'  - {ScheduleOccurrence.objects.count()} schedule occurrences')
        self.stdout.write(f'  - {OperatorUser.objects.count()} operators')
        self.stdout.write(f'  - {OperatorAssignment.objects.count()} operator assignments')
        self.stdout.write(f'  - {Booking.objects.count()} bookings')
        self.stdout.write('\nOperator credentials:')
        self.stdout.write('  Username: operator1, Password: operator123')
        self.stdout.write('  Username: operator2, Password: operator123')

