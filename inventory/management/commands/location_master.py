from django.core.management.base import BaseCommand
from inventory.models import LocationMaster, StockDetail


class Command(BaseCommand):
    help = 'Management command for LocationMaster operations'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help='Action: REGISTER or UNREGISTER')
        parser.add_argument('location_id', type=str, help='Location ID')

    def handle(self, *args, **options):
        action = options['action'].upper()
        location_id = options['location_id']

        if action == 'REGISTER':
            self.register_location(location_id)
        elif action == 'UNREGISTER':
            self.unregister_location(location_id)
        else:
            self.stdout.write(self.style.ERROR(f'Invalid action: {action}. Use REGISTER or UNREGISTER'))

    def register_location(self, location_id):
        """
        LOCATION REGISTER <LOCATION_ID>
        - Registers a new location
        - Fails if the location already exists
        """
        try:
            loc_obj = LocationMaster.objects.filter(location=location_id).first()
            
            if loc_obj:
                if loc_obj.status:
                    self.stdout.write(self.style.ERROR(f'LOCATION_REGISTER_FAILED: Location {location_id} already exists'))
                else:
                    # Reactivate inactive location
                    loc_obj.status = True
                    loc_obj.save()
                    self.stdout.write(self.style.SUCCESS(f'LOCATION_REGISTERED: {location_id}'))
                return

            # Create new location
            location = LocationMaster.objects.create(
                location=location_id,
                status=True
            )
            self.stdout.write(self.style.SUCCESS(f'LOCATION_REGISTERED: {location.location}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'LOCATION_REGISTER_FAILED: {str(e)}'))

    def unregister_location(self, location_id):
        """
        LOCATION UNREGISTER <LOCATION_ID>
        - Deregisters a location
        - Fails if the location doesn't exist or has any inventory
        """
        try:
            # Check if location exists
            try:
                location = LocationMaster.objects.get(location=location_id)
            except LocationMaster.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'LOCATION_UNREGISTER_FAILED: Location {location_id} does not exist'))
                return

            # Check if location has any inventory
            stock_objs = StockDetail.objects.filter(location=location, quantity__gt=0)
            if stock_objs.exists():
                self.stdout.write(self.style.ERROR(
                    f'LOCATION_UNREGISTER_FAILED: Location {location_id} has {stock_objs.count()} inventory record(s)'
                ))
                return

            # Delete location
            location.status = False
            location.save()
            self.stdout.write(self.style.SUCCESS(f'LOCATION_UNREGISTERED: {location_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'LOCATION_UNREGISTER_FAILED: {str(e)}'))
