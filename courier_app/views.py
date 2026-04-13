from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .models import Shipment, SupportTicket, ShipmentSubscriber

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def features(request):
    return render(request, 'features.html')

def tracking(request):
    return render(request, 'tracking.html')

def testimonials(request):
    return render(request, 'testimonials.html')

def contact(request):
    return render(request, 'contact.html')

def track_shipment(request, tracking_number):
    try:
        shipment = Shipment.objects.prefetch_related('events').get(tracking_number=tracking_number)
        status_name = shipment.status.name if shipment.status else "Unassigned"
        marker_color = shipment.status.marker_color if shipment.status else "gray"
        
        history_data = [
            {
                'status': event.status_name,
                'location': event.location or "System Data Center",
                'description': event.description or "",
                'time': event.timestamp.strftime('%b %d, %I:%M %p')
            } for event in shipment.events.all()
        ]
        
        # Fallback for legacy shipments that haven't recorded a timeline yet
        if not history_data:
            history_data.append({
                'status': status_name,
                'location': shipment.current_location_name or shipment.origin,
                'description': shipment.latest_update or "Status updated",
                'time': shipment.updated_at.strftime('%b %d, %I:%M %p')
            })
        
        return JsonResponse({
            'success': True,
            'tracking_number': shipment.tracking_number,
            'airway_bill': shipment.airway_bill_number or "AWB-PENDING",
            'status': status_name,
            'status_sort_order': shipment.status.sort_order if shipment.status else 0,
            'marker_color': marker_color,
            'origin': shipment.origin,
            'destination': shipment.destination,
            'current_location_name': shipment.current_location_name,
            'sender_name': shipment.sender_name,
            'sender_address': shipment.sender_address or "Not Provided",
            'receiver_name': shipment.receiver_name,
            'receiver_address': shipment.receiver_address or "Not Provided",
            'weight_kg': str(shipment.weight_kg),
            'content': shipment.package_content or "General Merchandise",
            'description': shipment.package_description or "No description provided.",
            'shipping_cost': f"${shipment.shipping_cost}",
            'estimated_delivery': shipment.estimated_delivery.strftime('%B %d, %Y'),
            'created_at': shipment.created_at.strftime('%B %d, %Y'),
            'latest_update': shipment.latest_update,
            'history': history_data,
            'origin_lat': shipment.origin_lat,
            'origin_lng': shipment.origin_lng,
            'dest_lat': shipment.dest_lat,
            'dest_lng': shipment.dest_lng,
            'current_lat': shipment.current_lat,
            'current_lng': shipment.current_lng
        })
    except Shipment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tracking number not found.'}, status=404)

def quote_view(request):
    return render(request, 'quote.html')

def help_center_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        tracking = request.POST.get('tracking', '')
        subject = request.POST.get('subject')
        issue = request.POST.get('issue')
        
        if email and subject and issue:
            SupportTicket.objects.create(
                customer_email=email,
                tracking_reference=tracking,
                subject=subject,
                issue_description=issue
            )
            messages.success(request, "Your support ticket has been submitted successfully. Our team will contact you shortly.")
            return redirect('help_center')
        else:
            messages.error(request, "Please fill out all required fields.")
            
    return render(request, 'help_center.html')

@csrf_exempt
def api_calculate_quote(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            weight = float(data.get('weight', 0))
            length = float(data.get('length', 0))
            width = float(data.get('width', 0))
            height = float(data.get('height', 0))
            
            # Basic volume weight calculation
            vol_weight = (length * width * height) / 5000
            billable_weight = max(weight, vol_weight)
            
            base_rate = 15.00
            cost_per_kg = 4.50
            
            standard_cost = base_rate + (billable_weight * cost_per_kg)
            express_cost = standard_cost * 1.5
            overnight_cost = standard_cost * 2.2
            
            return JsonResponse({
                'success': True,
                'standard': f"${standard_cost:.2f}",
                'express': f"${express_cost:.2f}",
                'overnight': f"${overnight_cost:.2f}",
                'billable_weight': f"{billable_weight:.2f} kg"
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def api_subscribe_tracking(request, tracking_number):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'success': False, 'message': 'Email is required.'})
                
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            subscriber, created = ShipmentSubscriber.objects.get_or_create(shipment=shipment, email=email)
            if created:
                from django.core.mail import send_mail
                from django.conf import settings
                subject = f"TransGlo: Subscription Confirmed for {shipment.tracking_number}"
                message = f"Hello,\n\nYou have successfully subscribed to live tracking updates for shipment {shipment.tracking_number}.\n\nWe will notify you immediately whenever the status changes.\n\nThank you,\nTransGlo Logistics Network"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
            return JsonResponse({'success': True, 'message': 'Successfully subscribed to updates!'})
        except Shipment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Tracking number not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
