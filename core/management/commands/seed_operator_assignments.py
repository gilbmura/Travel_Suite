from django.core.management.base import BaseCommand, CommandError

from core.models import OperatorProfile, OperatorAssignment, Route


class Command(BaseCommand):
    help = "Seed operator-to-route assignments so operator-scoped endpoints work."

    def add_arguments(self, parser):
        parser.add_argument(
            '--operator',
            help='Username of the operator to assign (default: all operators).'
        )
        parser.add_argument(
            '--routes',
            nargs='+',
            type=int,
            help='One or more route IDs to assign (default: all routes).'
        )

    def handle(self, *args, **options):
        operator_qs = OperatorProfile.objects.select_related('user').filter(user__is_operator=True)
        if options['operator']:
            operator_qs = operator_qs.filter(user__username=options['operator'])
            if not operator_qs.exists():
                raise CommandError(f"No operator found with username '{options['operator']}'.")

        route_qs = Route.objects.all()
        if options['routes']:
            route_qs = route_qs.filter(id__in=options['routes'])
            missing = set(options['routes']) - set(route_qs.values_list('id', flat=True))
            if missing:
                raise CommandError(f"Route ID(s) not found: {', '.join(str(r) for r in missing)}")

        if not operator_qs.exists():
            self.stdout.write(self.style.WARNING('No operators matched the provided filters.'))
            return
        if not route_qs.exists():
            self.stdout.write(self.style.WARNING('No routes available to assign.'))
            return

        created = 0
        for operator in operator_qs:
            for route in route_qs:
                _, was_created = OperatorAssignment.objects.get_or_create(operator=operator, route=route)
                if was_created:
                    created += 1
        self.stdout.write(self.style.SUCCESS(f"Assignments complete. {created} new link(s) created."))

