import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courier_project.settings')
django.setup()

from courier_app.models import Shipment, CustomStatus, TrackingEvent

status_events = [
    ("Order Received", "System", "Customer has placed the order, awaiting processing"),
    ("Payment Confirmed", "System", "Payment has been verified and approved"),
    ("Processing", "Warehouse", "Order is being prepared for shipment"),
    ("Label Created", "Warehouse", "Shipping label has been generated, tracking number assigned"),
    ("Awaiting Pickup", "Warehouse", "Package is ready, waiting for carrier to collect"),
    # Stage 2: Pickup & Origin Handling
    ("Picked Up", "Shipper Location", "Carrier has collected the package from shipper"),
    ("Received at Facility", "Origin Facility", "Package has arrived at origin shipping facility"),
    ("Processed at Facility", "Origin Facility", "Package has been scanned and sorted at origin facility"),
    ("Departure Scan", "Origin Facility", "Package has left the origin facility"),
    # Stage 3: In Transit
    ("In Transit", "In Transit", "Package is moving through the network"),
    ("Arrived at Hub", "Major Hub", "Package has reached a major sorting hub"),
    ("Departed Hub", "Major Hub", "Package has left the sorting hub"),
    ("Transfer to Destination Facility", "Logistics Network", "Package is being moved to destination region"),
    ("Customs Clearance (International)", "Customs Checkpoint", "Package is undergoing customs processing (for global shipments)"),
    ("Customs Hold", "Customs Checkpoint", "Package is delayed due to customs documentation (admin can update manually)"),
    ("Customs Released", "Customs Checkpoint", "Package has cleared customs and continues transit"),
    # Stage 4: Destination Region
    ("Arrived at Destination Facility", "Local Facility", "Package has reached the local facility near recipient"),
    ("Processed at Destination Facility", "Local Facility", "Package has been scanned and sorted at local facility"),
    ("Loaded onto Delivery Vehicle", "Local Facility", "Package is on the truck for final delivery"),
    # Stage 5: Out for Delivery
    ("Out for Delivery", "Destination Area", "Driver is en route with the package"),
    ("Delivery Attempted", "Recipient Location", "Driver tried but could not deliver (admin can add reason)"),
    ("Rescheduled for Delivery", "Local Office", "New delivery attempt scheduled"),
    # Stage 6: Final Delivery
    ("Delivered", "Recipient Location", "Package has been successfully delivered"),
    ("Delivered - Signed by", "Recipient Location", "Package delivered with signature (recipient name)"),
    ("Delivered - Left at", "Recipient Location", "Package left at specified location (porch, locker, neighbor)"),
    ("Proof of Delivery Available", "System", "Delivery confirmation photo or document is available"),
]

final_status, _ = CustomStatus.objects.get_or_create(name="Proof of Delivery Available", defaults={'marker_color': 'gray', 'sort_order': 260})

s, _ = Shipment.objects.update_or_create(
    tracking_number="TEST-FULL",
    defaults={
        'sender_name': "Mega Store",
        'sender_address': "101 Warehouse Dr, TX",
        'receiver_name': "Happy Customer",
        'receiver_address': "Home 54, NY",
        'origin': "Texas, USA",
        'destination': "New York, USA",
        'status': final_status,
        'weight_kg': 2.50,
        'package_content': "Gift Items",
        'estimated_delivery': datetime.date.today(),
        'latest_update': "Complete 26-stage lifecycle simulation applied!"
    }
)

# Clear existing to prevent duplicate append on re-runs
s.events.all().delete()

base_time = timezone.now() - datetime.timedelta(days=10)

for idx, (status, location, desc) in enumerate(status_events):
    event_time = base_time + datetime.timedelta(hours=idx*4) 
    event = TrackingEvent.objects.create(
        shipment=s,
        status_name=status,
        location=location,
        description=desc,
        sort_order=idx,
    )
    # Manually overwrite the auto_now_add field
    event.timestamp = event_time
    event.save(update_fields=['timestamp'])

print(f"Created Shipment '{s.tracking_number}' safely with all 26 custom lifecycle stages!")
