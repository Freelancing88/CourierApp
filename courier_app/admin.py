from django.contrib import admin
from .models import Shipment, CustomStatus, SupportTicket, ShipmentSubscriber, TrackingEvent

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1
    fields = ('status_name', 'location', 'description', 'timestamp', 'sort_order')
    readonly_fields = ('timestamp',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'customer_email', 'tracking_reference', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer_email', 'tracking_reference', 'subject')

@admin.register(ShipmentSubscriber)
class ShipmentSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'shipment', 'created_at')
    search_fields = ('email', 'shipment__tracking_number')

@admin.register(CustomStatus)
class CustomStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'marker_color')

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'sender_name', 'receiver_name', 'status', 'estimated_delivery')
    search_fields = ('tracking_number', 'sender_name', 'receiver_name')
    list_filter = ('status',)
    inlines = [TrackingEventInline]
    
    fieldsets = (
        ('Shipment Details', {
            'fields': (
                'tracking_number', 'airway_bill_number', 'weight_kg', 
                'package_content', 'package_description', 'shipping_cost', 'estimated_delivery'
            )
        }),
        ('Sender & Receiver', {
            'fields': (
                'sender_name', 'sender_address',
                'receiver_name', 'receiver_address'
            )
        }),
        ('Route Information', {
            'fields': (
                ('origin', 'origin_lat', 'origin_lng'),
                ('destination', 'dest_lat', 'dest_lng')
            )
        }),
        ('Update Shipment Location', {
            'fields': (
                'status',
                'current_location_name',
                ('current_lat', 'current_lng'),
                'latest_update'
            ),
            'description': "MANUAL UPDATE: Choose the status, set the text location, provide map coordinates, and provide an update log for the customer tracker."
        }),
    )
