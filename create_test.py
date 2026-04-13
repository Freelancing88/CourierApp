import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courier_project.settings')
django.setup()

from courier_app.models import Shipment, CustomStatus

# Find statuses
status_start = CustomStatus.objects.filter(name__icontains="Order Received").first()
status_end = CustomStatus.objects.filter(name__exact="Delivered").first()

if not status_start or not status_end:
    print("Ensure you have run seed_statuses.py first.")
    exit(1)

# Create Order Received shipment
s1, _ = Shipment.objects.update_or_create(
    tracking_number="TEST-ORDER",
    defaults={
        'sender_name': "John Doe",
        'sender_address': "123 Test Ave, NY",
        'receiver_name': "Jane Smith",
        'receiver_address': "456 Mockingbird Ln, CA",
        'origin': "New York",
        'destination': "Los Angeles",
        'status': status_start,
        'weight_kg': 5.00,
        'package_content': "Testing Material",
        'estimated_delivery': datetime.date.today() + datetime.timedelta(days=3),
        'latest_update': "ORDER RECEIVED - waiting for processing."
    }
)
print(f"Created Shipment '{s1.tracking_number}' with status '{s1.status.name}'.")

# Create Delivered shipment
s2, _ = Shipment.objects.update_or_create(
    tracking_number="TEST-DELIVERED",
    defaults={
        'sender_name': "Alpha Corp",
        'sender_address': "900 Market St, SF",
        'receiver_name': "Beta Inc",
        'receiver_address': "800 Broad St, TX",
        'origin': "San Francisco",
        'destination': "Austin",
        'status': status_end,
        'weight_kg': 15.00,
        'package_content': "Server Racks",
        'estimated_delivery': datetime.date.today(),
        'latest_update': "ORDER DELIVERED for testing - Signed by Receiver."
    }
)
print(f"Created Shipment '{s2.tracking_number}' with status '{s2.status.name}'.")
