import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courier_project.settings')
django.setup()

from courier_app.models import Shipment, CustomStatus, TrackingEvent

# Get or create custom status
status_in_transit, _ = CustomStatus.objects.get_or_create(
    name="IN TRANSIT / SECURE",
    defaults={'marker_color': 'red', 'sort_order': 50}
)

def create_diplomatic_shipment(tnum, ref_id):
    s, _ = Shipment.objects.update_or_create(
        tracking_number=tnum,
        defaults={
            'reference_id': ref_id,
            'is_diplomatic': True,
            'sender_name': "Embassy of Canada, Washington D.C.",
            'sender_address': "501 Pennsylvania Ave NW, Washington, DC 20001",
            'receiver_name': "High Commission of Canada, London",
            'receiver_address': "Canada House, Trafalgar Square, London SW1Y 5BJ",
            'origin': "Washington D.C., USA",
            'destination': "London, UK",
            'current_location_name': "In Transit (Flight CAN-101)",
            'status': status_in_transit,
            'weight_kg': 14.50,
            'package_content': "Classified Diplomatic Documents & Pouch Seals",
            'package_description': "Strict chain of custody diplomatic transfer. Seal #DP-CAN-9812.",
            'shipping_cost': 0.00,
            'origin_lat': 38.8951,
            'origin_lng': -77.0364,
            'current_lat': 48.8566,
            'current_lng': -20.1416,
            'dest_lat': 51.5074,
            'dest_lng': -0.1278,
            'estimated_delivery': datetime.date(2026, 9, 5),
            'latest_update': "Secure air transfer en route from Washington D.C. to London."
        }
    )
    
    s.events.all().delete()
    
    events_data = [
        {
            'status_name': 'POUCH MANIFESTED',
            'location': 'Embassy of Canada, Washington D.C.',
            'description': 'Diplomatic pouch verified and sealed by diplomatic courier team.',
            'time': timezone.make_aware(datetime.datetime(2026, 9, 4, 9, 0)),
            'verification_badge': 'VERIFIED: COURIER SECTION',
            'transport_type': 'courier',
            'sort_order': 10
        },
        {
            'status_name': 'DEPARTED EMBASSY',
            'location': 'Washington D.C., USA',
            'description': 'Escorted under armed tactical transport to Joint Base Andrews air terminal.',
            'time': timezone.make_aware(datetime.datetime(2026, 9, 4, 10, 30)),
            'verification_badge': 'SECURE ESCORT VERIFIED',
            'transport_type': 'armored',
            'sort_order': 20
        },
        {
            'status_name': 'EN ROUTE (SECURE AIR TRANSFER)',
            'location': 'In Transit (Flight CAN-101)',
            'description': 'Boarded secure diplomatic flight CAN-101 heading to London Heathrow / High Commission.',
            'time': timezone.make_aware(datetime.datetime(2026, 9, 5, 14, 45)),
            'verification_badge': 'HIGH SECURITY AIR TRANSFER',
            'transport_type': 'air',
            'sort_order': 50
        },
        {
            'status_name': 'ARRIVAL AT HIGH COMMISSION',
            'location': 'London, UK',
            'description': 'Scheduled hand-off and verification at Canada House, London.',
            'time': timezone.make_aware(datetime.datetime(2026, 9, 5, 17, 0)),
            'verification_badge': 'ESTIMATED ARRIVAL',
            'transport_type': 'embassy',
            'sort_order': 90
        }
    ]
    
    for ed in events_data:
        e = TrackingEvent.objects.create(
            shipment=s,
            status_name=ed['status_name'],
            location=ed['location'],
            description=ed['description'],
            verification_badge=ed['verification_badge'],
            transport_type=ed['transport_type'],
            sort_order=ed['sort_order']
        )
        e.timestamp = ed['time']
        e.save(update_fields=['timestamp'])
        
    print("Seeded diplomatic shipment successfully")

create_diplomatic_shipment("DP-CAN-9812-alpha", "DP-CAN-9812-alpha")
create_diplomatic_shipment("XB3713635315U", "DP-CAN-9812-alpha")
