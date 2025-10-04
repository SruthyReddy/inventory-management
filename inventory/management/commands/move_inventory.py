from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from inventory.models import MoveInventory, StockDetail, LocationMaster


class Command(BaseCommand):
    help = 'Management command for MoveInventory operations'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help='Action: TRANSFER')
        parser.add_argument('src_location_id', type=str, help='Source Location ID')
        parser.add_argument('dest_location_id', type=str, help='Destination Location ID')
        parser.add_argument('item_id', type=str, help='Item/SKU ID')
        parser.add_argument('quantity', type=int, help='Quantity to transfer')

    def handle(self, *args, **options):
        action = options['action'].upper()
        src_location_id = options['src_location_id']
        dest_location_id = options['dest_location_id']
        item_id = options['item_id']
        quantity = options['quantity']

        if action == 'TRANSFER':
            self.transfer_inventory(src_location_id, dest_location_id, item_id, quantity)
        else:
            self.stdout.write(self.style.ERROR(f'Invalid action: {action}. Use TRANSFER'))

    def transfer_inventory(self, src_location_id, dest_location_id, item_id, quantity):
        """
        INVENTORY TRANSFER <SRC_LOCATION_ID> <DEST_LOCATION_ID> <ITEM_ID> <QUANTITY>
        - Moves the quantity of the item from source to destination
        - Adds to target if the item doesn't exist there
        - Fails if either location doesn't exist, or source has insufficient quantity
        """
        try:
            with transaction.atomic():
                # Fetch both locations in a single query
                locations = LocationMaster.objects.filter(
                    location__in=[src_location_id, dest_location_id],
                    status=True
                )
                
                # Create a dictionary for easy lookup
                location_dict = {loc.location: loc for loc in locations}
                
                # Validate source location
                if src_location_id not in location_dict:
                    self.stdout.write(self.style.ERROR(f'INVENTORY_TRANSFER_FAILED: Source location {src_location_id} does not exist or is inactive'))
                    return
                
                # Validate destination location
                if dest_location_id not in location_dict:
                    self.stdout.write(self.style.ERROR(f'INVENTORY_TRANSFER_FAILED: Destination location {dest_location_id} does not exist or is inactive'))
                    return
                
                source = location_dict[src_location_id]
                destination = location_dict[dest_location_id]

                # Check if source and destination are different
                if source == destination:
                    self.stdout.write(self.style.ERROR('INVENTORY_TRANSFER_FAILED: Source and destination locations must be different'))
                    return

                # Check if quantity is positive
                if quantity <= 0:
                    self.stdout.write(self.style.ERROR('INVENTORY_TRANSFER_FAILED: Quantity must be positive'))
                    return

                # Check if stock exists at source
                try:
                    source_stock = StockDetail.objects.get(sku_code=item_id, location=source)
                except StockDetail.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'INVENTORY_TRANSFER_FAILED: Item {item_id} does not exist at source location {src_location_id}'))
                    return

                # Check if sufficient quantity exists at source
                if source_stock.quantity < quantity:
                    self.stdout.write(self.style.ERROR(
                        f'INVENTORY_TRANSFER_FAILED: Insufficient quantity at {src_location_id}. Available: {source_stock.quantity}, Required: {quantity}'
                    ))
                    return

                # Decrement source stock
                source_stock.quantity -= quantity
                source_stock.save()

                # Increment destination stock (create if doesn't exist)
                dest_stock, created = StockDetail.objects.get_or_create(
                    sku_code=item_id,
                    location=destination,
                    defaults={'quantity': quantity, 'original_quantity': quantity}
                )

                if not created:
                    dest_stock.quantity += quantity
                    dest_stock.save()

                # Create move record
                MoveInventory.objects.create(
                    sku_code=item_id,
                    source_location=source,
                    destination_location=destination,
                    quantity=quantity
                )

                self.stdout.write(self.style.SUCCESS('OK'))

        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_TRANSFER_FAILED: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'INVENTORY_TRANSFER_FAILED: {str(e)}'))
