from django.db import models
from django.core.exceptions import ValidationError


class LocationMaster(models.Model):
    """Model for managing warehouse locations"""
    location = models.CharField(max_length=200, unique=True)
    status = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'LOCATION_MASTER'
        index_together = ['location', 'status']

    def __str__(self):
        return self.location


class StockDetail(models.Model):
    """Model for tracking stock details at specific locations"""
    sku_code = models.CharField(max_length=100)
    location = models.ForeignKey(LocationMaster, on_delete=models.CASCADE, related_name='stock_details')
    quantity = models.IntegerField(default=0)
    original_quantity = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'STOCK_DETAIL'
        unique_together = ['sku_code', 'location']
        index_together = ['sku_code', 'location', 'quantity']

    def __str__(self):
        return f"{self.sku_code} @ {self.location.location}: {self.quantity}"

    def save(self, *args, **kwargs):
        """Override save to validate that location is active and quantities are non-negative"""
        if not self.location.status:
            raise ValidationError(f"Cannot create/update stock for inactive location: {self.location.location}")

        if self.quantity < 0:
            raise ValidationError(f"Quantity cannot be negative. Current value: {self.quantity}")

        if self.original_quantity < 0:
            raise ValidationError(f"Original quantity cannot be negative. Current value: {self.original_quantity}")

        super().save(*args, **kwargs)


class MoveInventory(models.Model):
    """Model for tracking inventory movements between locations"""
    sku_code = models.CharField(max_length=100)
    source_location = models.ForeignKey(LocationMaster, on_delete=models.CASCADE, related_name='outbound_moves')
    destination_location = models.ForeignKey(LocationMaster, on_delete=models.CASCADE, related_name='inbound_moves')
    quantity = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'MOVE_INVENTORY'

    def __str__(self):
        return f"{self.sku_code}: {self.source_location.location} → {self.destination_location.location} ({self.quantity})"
