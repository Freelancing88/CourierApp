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
    initial_track = request.GET.get('track') or request.GET.get('ref') or ''
    return render(request, 'tracking.html', {'initial_track': initial_track})

def tracking_with_number(request, tracking_number=''):
    return render(request, 'tracking.html', {'initial_track': tracking_number})

def testimonials(request):
    return render(request, 'testimonials.html')

def contact(request):
    return render(request, 'contact.html')

from django.db.models import Q

def track_shipment(request, tracking_number):
    try:
        shipment = Shipment.objects.prefetch_related('events').filter(
            Q(tracking_number__iexact=tracking_number) | Q(reference_id__iexact=tracking_number)
        ).order_by('-id').first()
        if not shipment:
            raise Shipment.DoesNotExist
        status_name = shipment.status.name if shipment.status else "Unassigned"
        marker_color = shipment.status.marker_color if shipment.status else "gray"
        
        history_data = []
        for event in shipment.events.all().order_by('sort_order', 'timestamp'):
            # Format cleanly like '09:00 EST' or '14:45 GMT'
            t_str = ""
            d_str = ""
            if event.timestamp:
                tz_name = event.timestamp.strftime('%Z')
                if not tz_name or tz_name == 'UTC':
                    tz_name = "GMT"
                t_str = f"{event.timestamp.strftime('%H:%M')} {tz_name}"
                d_str = event.timestamp.strftime('%b %d, %Y').upper()

            history_data.append({
                'id': event.id,
                'status': event.status_name,
                'location': event.location or "System Data Center",
                'description': event.description or "",
                'time': f"{d_str} | {t_str}" if d_str else "",
                'time_only': t_str,
                'date_only': d_str,
                'verification_badge': event.verification_badge or "",
                'transport_type': event.transport_type or "courier",
                'sort_order': event.sort_order,
            })
        
        # Fallback for legacy shipments that haven't recorded a timeline yet
        if not history_data:
            history_data.append({
                'id': 0,
                'status': status_name,
                'location': shipment.current_location_name or shipment.origin,
                'description': shipment.latest_update or "Status updated",
                'time': shipment.updated_at.strftime('%b %d, %Y | %H:%M %Z'),
                'time_only': shipment.updated_at.strftime('%H:%M %Z'),
                'date_only': shipment.updated_at.strftime('%b %d, %Y').upper(),
                'verification_badge': "VERIFIED: COURIER SECTION" if shipment.is_diplomatic else "",
                'transport_type': "courier",
                'sort_order': 0,
            })
        
        return JsonResponse({
            'success': True,
            'tracking_number': shipment.tracking_number,
            'reference_id': shipment.reference_id or f"DP-{shipment.tracking_number}",
            'is_diplomatic': shipment.is_diplomatic,
            'airway_bill': shipment.airway_bill_number or "AWB-PENDING",
            'status': status_name,
            'status_sort_order': shipment.status.sort_order if shipment.status else 0,
            'marker_color': marker_color,
            'origin': shipment.origin,
            'destination': shipment.destination,
            'current_location_name': shipment.current_location_name,
            'sender_name': shipment.sender_name,
            'sender_address': shipment.sender_address or "Not Provided",
            'sender_phone': "+86 138 0000 0000" if "GB456789123" in shipment.tracking_number else "+1 800 555 0199",
            'receiver_name': shipment.receiver_name,
            'receiver_address': shipment.receiver_address or "Not Provided",
            'receiver_phone': "+1 310 555 0123" if "GB456789123" in shipment.tracking_number else "+1 310 555 0123",
            'dimensions': "30x20x15 cm",
            'service_type': "Express" if not shipment.is_diplomatic else "Diplomatic Courier Escort",
            'weight_kg': str(shipment.weight_kg),
            'content': shipment.package_content or ("Documents" if not shipment.is_diplomatic else "Diplomatic Manifest Documents"),
            'description': shipment.package_description or "High security diplomatic pouch chain of custody.",
            'shipping_cost': f"${shipment.shipping_cost}",
            'estimated_delivery': shipment.estimated_delivery.strftime('%b %d, %Y').upper(),
            'created_at': shipment.created_at.strftime('%b %d, %Y') if shipment.created_at else "",
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
        return JsonResponse({'success': False, 'message': 'Tracking number or Diplomatic Reference ID not found.'}, status=404)

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
