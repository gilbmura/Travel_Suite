"""
Management command to generate schedule occurrences for future dates.
This ensures that schedule occurrences are always available for booking.
Run this command daily (via cron) or manually to extend future occurrences.
"""
from django.core.management.base import BaseCommand
from datetime import date, timedelta
from bookings.models import ScheduleRecurrence, ScheduleOccurrence


class Command(BaseCommand):
    help = 'Generates schedule occurrences for future dates (next 60 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='Number of days ahead to generate occurrences (default: 60)',
        )
        parser.add_argument(
            '--extend-only',
            action='store_true',
            help='Only extend existing occurrences, do not create new ones for inactive recurrences',
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        extend_only = options['extend_only']
        
        self.stdout.write(f'Generating schedule occurrences for the next {days_ahead} days...')
        
        # Get all active recurrences (or all if not extend_only)
        if extend_only:
            recurrences = ScheduleRecurrence.objects.filter(is_active=True)
        else:
            recurrences = ScheduleRecurrence.objects.all()
        
        if not recurrences.exists():
            self.stdout.write(self.style.WARNING('No schedule recurrences found. Create some recurrences first.'))
            return
        
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        total_created = 0
        total_updated = 0
        
        for recurrence in recurrences:
            if not recurrence.is_active and not extend_only:
                self.stdout.write(
                    self.style.WARNING(f'Skipping inactive recurrence: {recurrence}')
                )
                continue
            
            # Check the latest occurrence date for this recurrence
            latest_occurrence = ScheduleOccurrence.objects.filter(
                recurrence=recurrence
            ).order_by('-date').first()
            
            # Start from today or the day after the latest occurrence
            if latest_occurrence and latest_occurrence.date >= today:
                start_date = latest_occurrence.date + timedelta(days=1)
            else:
                start_date = today
            
            # Generate occurrences up to end_date
            current_date = start_date
            created_count = 0
            
            while current_date <= end_date:
                # Check if occurrence already exists
                occurrence, created = ScheduleOccurrence.objects.get_or_create(
                    recurrence=recurrence,
                    date=current_date,
                    defaults={
                        'departure_time': recurrence.departure_time,
                        'arrival_time': recurrence.arrival_time,
                        'status': 'scheduled'
                    }
                )
                
                if created:
                    created_count += 1
                    total_created += 1
                else:
                    # Update existing occurrence if it was cancelled or needs refresh
                    if occurrence.status == 'cancelled':
                        occurrence.status = 'scheduled'
                        occurrence.departure_time = recurrence.departure_time
                        occurrence.arrival_time = recurrence.arrival_time
                        occurrence.save()
                        total_updated += 1
                
                # Move to next day (for daily) or next week (for weekly)
                if recurrence.recurrence_type == 'daily':
                    current_date += timedelta(days=1)
                elif recurrence.recurrence_type == 'weekly':
                    current_date += timedelta(days=7)
                else:
                    # Default to daily
                    current_date += timedelta(days=1)
            
            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created {created_count} occurrences for {recurrence} '
                        f'({start_date} to {min(end_date, current_date - timedelta(days=1))})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {total_created} new occurrences, '
                f'updated {total_updated} existing occurrences.'
            )
        )

