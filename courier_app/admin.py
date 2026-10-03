from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Shipment, CustomStatus, SupportTicket, ShipmentSubscriber, TrackingEvent

admin.site.site_header = "TransGlo Logistic Network — Admin Portal"
admin.site.site_title = "TransGlo Operations"
admin.site.index_title = "Courier & Diplomatic Pouch Management Console"

class TrackingEventInline(admin.TabularInline):
    model = TrackingEvent
    extra = 1
    fields = ('timestamp', 'status_name', 'location', 'transport_type', 'verification_badge', 'description', 'sort_order')
    classes = ('collapse',)
    verbose_name = "Tracking Checkpoint / Custody Event"
    verbose_name_plural = "Tracking Timeline Checkpoints"

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'customer_email', 'tracking_reference', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_email', 'tracking_reference', 'subject', 'issue_description')
    ordering = ('-created_at',)

@admin.register(ShipmentSubscriber)
class ShipmentSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'shipment_link', 'created_at')
    search_fields = ('email', 'shipment__tracking_number')
    ordering = ('-created_at',)

    def shipment_link(self, obj):
        if obj.shipment:
            return format_html(
                '<a href="/admin/courier_app/shipment/{}/change/">{}</a>',
                obj.shipment.id,
                obj.shipment.tracking_number
            )
        return "—"
    shipment_link.short_description = "Subscribed Shipment"

@admin.register(CustomStatus)
class CustomStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_badge', 'sort_order')
    ordering = ('sort_order', 'name')
    list_editable = ('sort_order',)

    def color_badge(self, obj):
        colors = {
            'green': '#10b981',
            'red': '#ef4444',
            'yellow': '#f59e0b',
            'gray': '#6b7280'
        }
        hex_col = colors.get(obj.marker_color, '#6b7280')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:3px 10px; border-radius:12px; font-weight:600; font-size:11px;">{}</span>',
            hex_col,
            obj.get_marker_color_display()
        )
    color_badge.short_description = "Status Marker Color"

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_badge',
        'type_badge',
        'status_badge',
        'sender_info',
        'receiver_info',
        'current_location_name',
        'estimated_delivery',
        'actions_buttons'
    )
    search_fields = (
        'tracking_number', 'reference_id', 'airway_bill_number',
        'sender_name', 'sender_phone', 'receiver_name', 'receiver_phone',
        'courier_phone', 'origin', 'destination', 'current_location_name'
    )
    list_filter = ('is_diplomatic', 'status', 'estimated_delivery', 'created_at')
    inlines = [TrackingEventInline]
    save_on_top = True
    
    fieldsets = (
        ('🛡️ Shipment Identity & Security Clearance', {
            'fields': (
                ('is_diplomatic', 'service_type'),
                ('tracking_number', 'reference_id', 'airway_bill_number'),
            ),
            'description': "Leave Tracking Number or AWB blank to auto-generate, or provide your custom reference (e.g. GB456789123)."
        }),
        ('👤 Sender (Shipper) Information', {
            'fields': (
                ('sender_name', 'sender_phone'),
                'sender_address',
            ),
            'description': "Contact phone number is displayed on the tracking page, label, and receipt."
        }),
        ('📦 Recipient (Consignee) Information', {
            'fields': (
                ('receiver_name', 'receiver_phone'),
                'receiver_address',
            ),
            'description': "Full recipient destination contact details."
        }),
        ('🚚 Courier Dispatch & Package Specifications', {
            'fields': (
                ('courier_phone', 'shipping_cost'),
                ('weight_kg', 'dimensions', 'pieces_count'),
                ('package_content', 'estimated_delivery'),
                'package_description'
            )
        }),
        ('📍 Current Telemetry & Live Status', {
            'fields': (
                ('status', 'current_location_name'),
                ('current_lat', 'current_lng'),
                'latest_update'
            ),
            'description': "Updating these fields automatically appends a new tracking timeline entry."
        }),
        ('🗺️ Route Coordinates (Origin & Final Destination)', {
            'fields': (
                ('origin', 'origin_lat', 'origin_lng'),
                ('destination', 'dest_lat', 'dest_lng'),
            ),
            'classes': ('collapse',),
            'description': "Used to plot the animated flight / transit route on the live map matrix."
        }),
    )

    def tracking_badge(self, obj):
        return format_html(
            '<div style="font-family:monospace; font-weight:700; font-size:13px; color:#1e3a8a;">'
            '{}'
            '<div style="font-size:10px; color:#64748b; font-weight:normal;">AWB: {}</div>'
            '</div>',
            obj.tracking_number,
            obj.airway_bill_number or "—"
        )
    tracking_badge.short_description = "Tracking / AWB"
    tracking_badge.admin_order_field = 'tracking_number'

    def type_badge(self, obj):
        if obj.is_diplomatic:
            return mark_safe(
                '<span style="background-color:#fee2e2; color:#b91c1c; border:1px solid #f87171; padding:3px 8px; border-radius:4px; font-weight:700; font-size:11px;">'
                '🛡️ DIPLOMATIC POUCH'
                '</span>'
            )
        return mark_safe(
            '<span style="background-color:#e0f2fe; color:#0369a1; border:1px solid #7dd3fc; padding:3px 8px; border-radius:4px; font-weight:600; font-size:11px;">'
            '📦 Standard Courier'
            '</span>'
        )
    type_badge.short_description = "Clearance / Type"
    type_badge.admin_order_field = 'is_diplomatic'

    def status_badge(self, obj):
        if not obj.status:
            return mark_safe('<span style="color:#94a3b8;">Unassigned</span>')
        colors = {
            'green': '#10b981',
            'red': '#ef4444',
            'yellow': '#f59e0b',
            'gray': '#6b7280'
        }
        bg = colors.get(obj.status.marker_color, '#6b7280')
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:4px 10px; border-radius:12px; font-weight:600; font-size:11px; white-space:nowrap;">'
            '{}'
            '</span>',
            bg,
            obj.status.name
        )
    status_badge.short_description = "Live Status"
    status_badge.admin_order_field = 'status__name'

    def sender_info(self, obj):
        phone_html = f"📞 {obj.sender_phone}" if obj.sender_phone else '<span style="color:#cbd5e1;">No phone</span>'
        return format_html(
            '<div><strong>{}</strong><div style="font-size:11px; color:#475569;">{}</div></div>',
            obj.sender_name,
            mark_safe(phone_html)
        )
    sender_info.short_description = "Sender & Phone"

    def receiver_info(self, obj):
        phone_html = f"📞 {obj.receiver_phone}" if obj.receiver_phone else '<span style="color:#cbd5e1;">No phone</span>'
        return format_html(
            '<div><strong>{}</strong><div style="font-size:11px; color:#475569;">{}</div></div>',
            obj.receiver_name,
            mark_safe(phone_html)
        )
    receiver_info.short_description = "Recipient & Phone"

    def actions_buttons(self, obj):
        return format_html(
            '<div style="display:flex; gap:4px; flex-wrap:nowrap;">'
            '<a href="/track/{}/" target="_blank" style="background:#2563eb; color:#fff; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:600;" title="View Live Tracking">🔍 Track</a>'
            '<a href="/track/{}/receipt/" target="_blank" style="background:#059669; color:#fff; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:600;" title="Download Receipt">📄 Receipt</a>'
            '<a href="/track/{}/label/" target="_blank" style="background:#d97706; color:#fff; padding:4px 8px; border-radius:4px; text-decoration:none; font-size:11px; font-weight:600;" title="Print Shipping Label">🏷️ Label</a>'
            '</div>',
            obj.tracking_number,
            obj.tracking_number,
            obj.tracking_number
        )
    actions_buttons.short_description = "Quick Actions"
