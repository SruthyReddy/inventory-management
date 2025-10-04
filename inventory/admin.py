from django.contrib import admin
from .models import LocationMaster, StockDetail, MoveInventory


@admin.register(LocationMaster)
class LocationMasterAdmin(admin.ModelAdmin):
    list_display = ['location', 'status', 'creation_date', 'updation_date']
    list_filter = ['status', 'creation_date']
    search_fields = ['location']
    readonly_fields = ['creation_date', 'updation_date']


@admin.register(StockDetail)
class StockDetailAdmin(admin.ModelAdmin):
    list_display = ['sku_code', 'location', 'quantity', 'original_quantity', 'creation_date', 'updation_date']
    list_filter = ['location', 'creation_date']
    search_fields = ['sku_code', 'location__location']
    readonly_fields = ['creation_date', 'updation_date']
    list_select_related = ['location']


@admin.register(MoveInventory)
class MoveInventoryAdmin(admin.ModelAdmin):
    list_display = ['sku_code', 'source_location', 'destination_location', 'quantity', 'creation_date']
    list_filter = ['source_location', 'destination_location', 'creation_date']
    search_fields = ['sku_code', 'source_location__location', 'destination_location__location']
    readonly_fields = ['creation_date', 'updation_date']
    list_select_related = ['source_location', 'destination_location']
