"""
Management command to seed initial data into the database.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from core.models import User, Customer, Route, Vehicle, Seat
from datetime import time


class Command(BaseCommand):
    help = 'Seed database with initial data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')

        # Create superuser/admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@travelsuite.com',
                password='Admin@123',
                phone_number='+250788111111',
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))
        else:
            self.stdout.write('Admin user already exists')

        # Create operator user
        if not User.objects.filter(username='operator').exists():
            operator = User.objects.create_user(
                username='operator',
                email='operator@travelsuite.com',
                password='Operator@123',
                phone_number='+250788222222',
                is_operator=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created operator user'))
        else:
            self.stdout.write('Operator user already exists')

        # Create sample customers
        if Customer.objects.count() == 0:
            customers_data = [
                {'name': 'John Doe', 'address': 'Kigali',
                    'phone_number': '+250788333333', 'national_id': '1234567890123456'},
                {'name': 'Jane Smith', 'address': 'Kigali',
                    'phone_number': '+250788444444', 'national_id': '1234567890123457'},
                {'name': 'Bob Johnson', 'address': 'Muhanga',
                    'phone_number': '+250788555555', 'national_id': '1234567890123458'},
            ]
            for data in customers_data:
                Customer.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created {len(customers_data)} customers'))
        else:
            self.stdout.write(
                f'Customers already exist: {Customer.objects.count()}')

        # Create sample routes
        if Route.objects.count() == 0:
            routes_data = [
                {
                    'origin': 'Nyabugogo',
                    'destination': 'Muhanga',
                    'departure_time': time(8, 0),
                    'arrival_time': time(9, 0),
                    'stops': 'Kimironko, Gisozi',
                    'fare': '5000.00'
                },
                {
                    'origin': 'Remera',
                    'destination': 'Gitarama',
                    'departure_time': time(10, 0),
                    'arrival_time': time(11, 30),
                    'stops': 'Kabeza',
                    'fare': '8000.00'
                },
                {
                    'origin': 'Nyabugogo',
                    'destination': 'Ruhengeri',
                    'departure_time': time(6, 0),
                    'arrival_time': time(9, 0),
                    'stops': 'Muhanga, Rwamagana',
                    'fare': '12000.00'
                },
            ]
            for data in routes_data:
                Route.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created {len(routes_data)} routes'))
        else:
            self.stdout.write(f'Routes already exist: {Route.objects.count()}')

        # Create sample vehicles with seats
        if Vehicle.objects.count() == 0:
            routes = Route.objects.all()
            vehicles_data = [
                {'license_plate': 'RW001BUS', 'route': routes.first(
                ), 'capacity': 50, 'status': 'Available'},
                {'license_plate': 'RW002BUS', 'route': routes[1] if len(
                    routes) > 1 else routes.first(), 'capacity': 45, 'status': 'Available'},
                {'license_plate': 'RW003BUS', 'route': routes[2] if len(
                    routes) > 2 else routes.first(), 'capacity': 60, 'status': 'Available'},
            ]
            for data in vehicles_data:
                vehicle = Vehicle.objects.create(**data)
                # Create seats for each vehicle
                for i in range(1, data['capacity'] + 1):
                    Seat.objects.create(vehicle=vehicle, seat_number=f"A{i}")
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created {len(vehicles_data)} vehicles with seats'))
        else:
            self.stdout.write(
                f'Vehicles already exist: {Vehicle.objects.count()}')

        self.stdout.write(self.style.SUCCESS(
            '✓ Database seeding completed successfully!'))
