from django.db import models
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.db.models.signals import pre_save
from django.dispatch import receiver
class CustomStatus(models.Model):
    COLOR_CHOICES = [
        ('green', 'Green (In Transit)'),
        ('red', 'Red (Stopped/Issue)'),
        ('yellow', 'Yellow (Waiting/Pending)'),
        ('gray', 'Gray (Delivered/Unknown)')
    ]
    name = models.CharField(max_length=100, unique=True, help_text="e.g. Out for Delivery, Customs Clearance")
    marker_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='gray')
    sort_order = models.IntegerField(default=100, help_text="Chronological order for dropdowns")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Custom Statuses"
        ordering = ['sort_order', 'name']

class Shipment(models.Model):
    tracking_number = models.CharField(max_length=20, unique=True, blank=True)
    airway_bill_number = models.CharField(max_length=50, blank=True, null=True, help_text="AWB Number")
    
    sender_name = models.CharField(max_length=100)
    sender_address = models.TextField(blank=True, null=True)
    receiver_name = models.CharField(max_length=100)
    receiver_address = models.TextField(blank=True, null=True)
    
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    current_location_name = models.CharField(max_length=100, default="Origin Sorting Hub", help_text="Type city/country manually.")
    
    status = models.ForeignKey(CustomStatus, on_delete=models.SET_NULL, null=True, blank=True)
    
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    package_content = models.CharField(max_length=200, blank=True, null=True)
    package_description = models.TextField(blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    origin_lat = models.FloatField(default=40.7128) 
    origin_lng = models.FloatField(default=-74.0060)
    dest_lat = models.FloatField(default=34.0522)   
    dest_lng = models.FloatField(default=-118.2437)
    
    current_lat = models.FloatField(default=40.7128)
    current_lng = models.FloatField(default=-74.0060)
    
    estimated_delivery = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    latest_update = models.TextField(default="Shipment logged in network.")

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"TRG-{get_random_string(8).upper()}"
        if not self.airway_bill_number:
            self.airway_bill_number = f"AWB-{get_random_string(10).upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        status_name = self.status.name if self.status else "Unassigned"
        return f"{self.tracking_number} - {status_name}"

class ShipmentSubscriber(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='subscribers')
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} -> {self.shipment.tracking_number}"

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
    ]
    tracking_reference = models.CharField(max_length=20, blank=True, null=True, help_text="Optional TRG/AWB number")
    customer_email = models.EmailField()
    subject = models.CharField(max_length=200)
    issue_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id}: {self.subject} ({self.status})"

@receiver(pre_save, sender=Shipment)
def notify_subscribers_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Shipment.objects.get(pk=instance.pk)
            # Check if status changed
            if old_instance.status != instance.status:
                # We need to fetch subscribers. Since we are in pre_save, related managers might be tricky,
                # but instance.pk exists, so instance.subscribers.all() is safe.
                subscribers = list(instance.subscribers.all().values_list('email', flat=True))
                if subscribers:
                    status_name = instance.status.name if instance.status else "Unassigned"
                    subject = f"TransGlo Update: Shipment {instance.tracking_number} - {status_name}"
                    message = f"Hello,\n\nYour shipment {instance.tracking_number} has an updated status: {status_name}.\n\nLatest update notes: {instance.latest_update}\n\nThank you for choosing TransGlo Logistics."
                    
                    send_mail(
                        subject,
                        message,
                        'noreply@transglo.com',
                        subscribers,
                        fail_silently=True,
                    )
        except Shipment.DoesNotExist:
            pass
