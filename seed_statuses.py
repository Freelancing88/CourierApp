import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'courier_project.settings')
django.setup()

from courier_app.models import CustomStatus

statuses_to_create = [
    # Stage 1
    ("Order Received", "yellow", 10),
    ("Payment Confirmed", "yellow", 20),
    ("Processing", "yellow", 30),
    ("Label Created", "yellow", 40),
    ("Awaiting Pickup", "yellow", 50),
    # Stage 2
    ("Picked Up", "green", 60),
    ("Received at Facility", "green", 70),
    ("Processed at Facility", "green", 80),
    ("Departure Scan", "green", 90),
    # Stage 3
    ("In Transit", "green", 100),
    ("Arrived at Hub", "green", 110),
    ("Departed Hub", "green", 120),
    ("Transfer to Destination Facility", "green", 130),
    ("Customs Clearance", "yellow", 140),
    ("Customs Hold", "red", 150),
    ("Customs Released", "green", 160),
    # Stage 4
    ("Arrived at Destination Facility", "green", 170),
    ("Processed at Destination Facility", "green", 180),
    ("Loaded onto Delivery Vehicle", "green", 190),
    # Stage 5
    ("Out for Delivery", "green", 200),
    ("Delivery Attempted", "red", 210),
    ("Rescheduled for Delivery", "yellow", 220),
    # Stage 6
    ("Delivered", "gray", 230),
    ("Delivered - Signed by", "gray", 240),
    ("Delivered - Left at", "gray", 250),
    ("Proof of Delivery Available", "gray", 260),
    # Stage 7 (Exceptions)
    ("Exception", "red", 500),
    ("Weather Delay", "red", 510),
    ("Address Issue", "red", 520),
    ("Recipient Not Available", "red", 530),
    ("Held at Facility", "red", 540),
    ("Return to Sender", "red", 550),
    ("Damaged in Transit", "red", 560),
    ("Lost", "red", 570),
]

for name, color, order in statuses_to_create:
    CustomStatus.objects.update_or_create(
        name=name,
        defaults={'marker_color': color, 'sort_order': order}
    )

print(f"Successfully seeded {len(statuses_to_create)} statuses.")
