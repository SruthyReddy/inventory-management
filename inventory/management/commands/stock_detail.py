from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from inventory.models import StockDetail, LocationMaster


class Command(BaseCommand):
    help = 'Management command for StockDetail operations'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help='Action: INCREMENT, DECREMENT, or OBSERVE')
        parser.add_argument('location_id', type=str, help='Location ID')
        parser.add_argument('item_id', type=str, nargs='?', help='Item/SKU ID (not required for OBSERVE)')
        parser.add_argument('quantity', type=int, nargs='?', help='Quantity (not required for OBSERVE)')

    def handle(self, *args, **options):
        action = options['action'].upper()
        location_id = options['location_id']
        item_id = options.get('item_id')
        quantity = options.get('quantity')

        if action == 'INCREMENT':
            self.increment_inventory(location_id, item_id, quantity)
        elif action == 'DECREMENT':
            self.decrement_inventory(location_id, item_id, quantity)
        elif action == 'OBSERVE':
            self.observe_inventory(location_id)
        else:
            self.stdout.write(self.style.ERROR(f'Invalid action: {action}. Use INCREMENT, DECREMENT, or OBSERVE'))


    def increment_inventory(self, location_id, item_id, quantity):
        """
        INVENTORY INCREMENT <LOCATION_ID> <ITEM_ID> <QUANTITY>
        - Adds the quantity to the item in the location
        - If the item doesn't exist, create it with that quantity
        - Fails if the location doesn't exist
        """
        try:
            # Check if location exists and is active
            try:
                location = LocationMaster.objects.get(location=location_id, status=True)
            except LocationMaster.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'INVENTORY_INCREMENT_FAILED: Location {location_id} does not exist'))
                return

            # Get or create stock record
            stock_obj, created = StockDetail.objects.get_or_create(
                sku_code=item_id,
                location=location,
                defaults={'quantity': quantity, 'original_quantity': quantity}
            )

            if not created:
                stock_obj.quantity += quantity
                stock_obj.original_quantity += quantity
                stock_obj.save()

            self.stdout.write(self.style.SUCCESS(
                f'INVENTORY_INCREMENTED: {item_id} at {location_id}, new quantity: {stock_obj.quantity}'
            ))

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_INCREMENT_FAILED: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_INCREMENT_FAILED: {str(e)}'))

    def decrement_inventory(self, location_id, item_id, quantity):
        """
        INVENTORY DECREMENT <LOCATION_ID> <ITEM_ID> <QUANTITY>
        - Subtracts the quantity from the item in the location
        - Fails if the location doesn't exist, the item doesn't exist, or there's insufficient quantity
        """
        try:
            # Check if location exists
            try:
                location = LocationMaster.objects.get(location=location_id, status=True)
            except LocationMaster.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'INVENTORY_DECREMENT_FAILED: Location {location_id} does not exist'))
                return

            # Check if stock exists
            try:
                stock = StockDetail.objects.get(sku_code=item_id, location=location)
            except StockDetail.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'INVENTORY_DECREMENT_FAILED: Item {item_id} does not exist at location {location_id}'))
                return

            # Check if sufficient quantity exists
            if stock.quantity < quantity:
                self.stdout.write(self.style.ERROR(
                    f'INVENTORY_DECREMENT_FAILED: Insufficient quantity for {item_id} at {location_id}. Available: {stock.quantity}, Required: {quantity}'
                ))
                return

            # Decrement quantity
            old_quantity = stock.quantity
            stock.quantity -= quantity
            stock.save()

            self.stdout.write(self.style.SUCCESS(
                f'INVENTORY_DECREMENTED: {item_id} at {location_id} from {old_quantity} to {stock.quantity}'
            ))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_DECREMENT_FAILED: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_DECREMENT_FAILED: {str(e)}'))

    def observe_inventory(self, location_id):
        """
        INVENTORY OBSERVE <LOCATION_ID>
        - Outputs the inventories in the format: "ITEM <ITEM_ID> <QUANTITY>" for each item
        - One per line, sorted alphabetically by item_id
        - If no items, output "EMPTY"
        - Fails if the location doesn't exist
        """
        try:
            # Check if location exists
            try:
                location = LocationMaster.objects.get(location=location_id, status=True)
            except LocationMaster.DoesNotExist:
                self.stdout.write(f"ERR: Location '{location_id}' does not exist")
                return

            # Get all stock items at this location with quantity > 0, sorted by SKU
            stock_items = StockDetail.objects.filter(
                location=location,
                quantity__gt=0
            ).order_by('sku_code')

            # If no items, output EMPTY
            if not stock_items.exists():
                self.stdout.write('EMPTY')
                return

            # Output each item
            for stock in stock_items:
                self.stdout.write(f'ITEM {stock.sku_code} {stock.quantity}')

        except Exception as e:
            self.stdout.write(f"ERR: {str(e)}")
