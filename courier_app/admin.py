from django.contrib import admin
from .models import Shipment, CustomStatus, SupportTicket, ShipmentSubscriber, TrackingEvent

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1
    fields = ('timestamp', 'location', 'status_name', 'verification_badge', 'transport_type', 'description', 'sort_order')

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
    list_display = ('tracking_number', 'reference_id', 'sender_name', 'receiver_name', 'status', 'estimated_delivery', 'is_diplomatic')
    search_fields = ('tracking_number', 'reference_id', 'sender_name', 'receiver_name')
    list_filter = ('status', 'is_diplomatic')
    readonly_fields = ('tracking_number', 'airway_bill_number')
    inlines = [TrackingEventInline]
    
    fieldsets = (
        ('Shipment Identity & Security', {
            'fields': (
                'tracking_number', 'reference_id', 'is_diplomatic', 'airway_bill_number'
            )
        }),
        ('Package Details', {
            'fields': (
                'weight_kg', 'package_content', 'package_description', 'shipping_cost', 'estimated_delivery'
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
        ('Current Status & Location (Auto-updated by events)', {
            'fields': (
                'status',
                'current_location_name',
                ('current_lat', 'current_lng'),
                'latest_update'
            ),
            'description': "These fields summarize the current state. Detailed tracking events should be added below."
        }),
    )
