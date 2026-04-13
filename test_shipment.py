import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courier_project.settings')
django.setup()

from courier_app.models import Shipment, CustomStatus

status_end = CustomStatus.objects.filter(name__exact="Delivered").first()

if not status_end:
    print("Run seed_statuses.py first.")
    exit(1)

s, created = Shipment.objects.update_or_create(
    tracking_number="451-060-8531",
    defaults={
        'sender_name': "Global Logistics",
        'sender_address': "1028 Main St, NY",
        'receiver_name': "Tech Solutions",
        'receiver_address': "3049 Alpha Ave, CA",
        'origin': "New York, USA",
        'destination': "San Francisco, USA",
        'status': status_end,
        'weight_kg': 12.50,
        'package_content': "Network Switches",
        'estimated_delivery': datetime.date.today(),
        'latest_update': "Delivered - Signed by Tech Solutions Reception."
    }
)

if created:
    print(f"Created Shipment {s.tracking_number} with status 'Delivered'.")
else:
    print(f"Updated Shipment {s.tracking_number} to ensure it exists and is 'Delivered'.")
