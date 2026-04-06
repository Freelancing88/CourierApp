document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('mainNav');

    let shipmentMap = null;
    let marker = null;
    let destMarker = null;
    let pollingInterval = null;

    function renderMap(lat, lng, dLat, dLng, markerColor) {
        if (!shipmentMap) {
            shipmentMap = L.map('shipmentMap').setView([lat, lng], 5);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap'
            }).addTo(shipmentMap);
        } else {
            // clear existing markers
            if (marker) shipmentMap.removeLayer(marker);
            if (destMarker) shipmentMap.removeLayer(destMarker);
            
            // clear polyline by just removing polylines
            shipmentMap.eachLayer(function (layer) {
                if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
                    shipmentMap.removeLayer(layer);
                }
            });
        }

        let bootstrapColorClass = 'text-secondary';
        if (markerColor === 'green') bootstrapColorClass = 'text-success';
        if (markerColor === 'red') bootstrapColorClass = 'text-danger';
        if (markerColor === 'yellow') bootstrapColorClass = 'text-warning';

        var customIcon = L.divIcon({
            html: `<div style="transform:translate(-25%, -25%);"><i class="bi bi-check-circle-fill ${bootstrapColorClass}" style="font-size: 28px; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); background:white; border-radius:50%;"></i></div>`,
            iconSize: [28, 28],
            className: 'custom-status-marker'
        });

        marker = L.marker([lat, lng], { icon: customIcon }).addTo(shipmentMap);
        
        var dIcon = L.divIcon({
            html: `<div style="transform:translate(-25%, -25%);"><i class="bi bi-geo-alt-fill text-dark" style="font-size: 28px; filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.3)); background:white; border-radius:50%;"></i></div>`,
            iconSize: [28, 28],
            className: 'custom-status-marker'
        });
        destMarker = L.marker([dLat, dLng], { icon: dIcon }).addTo(shipmentMap);

        var latlngs = [[lat, lng], [dLat, dLng]];
        L.polyline(latlngs, { color: '#d32f2f', dashArray: '5, 10', weight: 3 }).addTo(shipmentMap);
        shipmentMap.fitBounds(latlngs, { padding: [50, 50] });
    }

    // Navbar visual change on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });



    // Order Tracking Logic
    const trackBtn = document.getElementById('trackBtn');
    const trackingInput = document.getElementById('trackingInput');
    const trackingResult = document.getElementById('trackingResult');

    if (trackBtn && trackingInput) {
        trackBtn.addEventListener('click', async () => {
            const code = trackingInput.value.trim();
            if (!code) return;

            // Step 1 - Loading State
            trackBtn.disabled = true;
            trackBtn.style.cursor = 'not-allowed';
            trackBtn.style.opacity = '0.7';
            trackBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Tracking information is loading...';

            try {
                // Step 2 - Delay 2 seconds
                await new Promise(resolve => setTimeout(resolve, 2000));

                const response = await fetch(`/api/track/${encodeURIComponent(code)}/`);
                const data = await response.json();

                trackingResult.classList.remove('d-none');

                if (data.success) {
                    document.getElementById('resStatus').innerText = data.status.toUpperCase();
                    document.getElementById('resEstDelivery').innerText = data.estimated_delivery;
                    document.getElementById('resOrigin').innerText = data.origin;
                    document.getElementById('resDest').innerText = data.destination;
                    document.getElementById('resUpdate').innerText = data.latest_update;
                    document.getElementById('resStatus').className = 'badge bg-yellow text-dark tracking-wide shadow-sm';

                    // Advanced Fields binding
                    if (document.getElementById('resAWB')) document.getElementById('resAWB').innerText = data.airway_bill;
                    if (document.getElementById('resCreated')) document.getElementById('resCreated').innerText = data.created_at;
                    if (document.getElementById('resContent')) document.getElementById('resContent').innerText = data.content;
                    if (document.getElementById('resWeight')) document.getElementById('resWeight').innerText = data.weight_kg;
                    if (document.getElementById('resCost')) document.getElementById('resCost').innerText = data.shipping_cost;
                    if (document.getElementById('resSenderName')) document.getElementById('resSenderName').innerText = data.sender_name;
                    if (document.getElementById('resSenderAddr')) document.getElementById('resSenderAddr').innerText = data.sender_address;
                    if (document.getElementById('resReceiverName')) document.getElementById('resReceiverName').innerText = data.receiver_name;
                    if (document.getElementById('resReceiverAddr')) document.getElementById('resReceiverAddr').innerText = data.receiver_address;

                    if (document.getElementById('shipmentMap')) {
                        renderMap(data.current_lat, data.current_lng, data.dest_lat, data.dest_lng, data.marker_color);
                        
                        // Hide outdated simulation labels completely
                        if(document.getElementById('resAvgSpeed')) document.getElementById('resAvgSpeed').parentElement.style.display = 'none';
                        if(document.getElementById('resEtaHours')) document.getElementById('resEtaHours').parentElement.style.display = 'none';

                        // fix map bounds after visibility change expands the container height
                        setTimeout(() => { if (shipmentMap) shipmentMap.invalidateSize(); }, 300);
                    }
                } else {
                    document.getElementById('resStatus').innerText = 'NOT FOUND';
                    document.getElementById('resOrigin').innerText = 'Unknown';
                    document.getElementById('resDest').innerText = 'Unknown';
                    document.getElementById('resUpdate').innerText = data.message;
                    document.getElementById('resEstDelivery').innerText = '-';
                    document.getElementById('resStatus').className = 'badge bg-danger text-white tracking-wide';
                }
                // Subscribe Logic Connection
                const subForm = document.getElementById('subscribeForm');
                if (subForm) {
                    // removing previous listeners implicitly via inner function logic isn't needed here, just assign onsubmit
                    subForm.onsubmit = async (e) => {
                        e.preventDefault();
                        const sBtn = document.getElementById('subBtn');
                        const sMsg = document.getElementById('subMessage');
                        sBtn.disabled = true;
                        
                        try {
                            const subRes = await fetch(`/api/track/${encodeURIComponent(code)}/subscribe/`, {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({ email: document.getElementById('subEmail').value })
                            });
                            
                            const subData = await subRes.json();
                            sMsg.innerText = subData.message;
                            sMsg.classList.remove('d-none');
                            if(subData.success) {
                                document.getElementById('subEmail').value = '';
                                sMsg.classList.replace('text-yellow', 'text-warning');
                            }
                        } catch(err) {
                            sMsg.innerText = "Connection error.";
                            sMsg.classList.remove('d-none');
                        } finally {
                            sBtn.disabled = false;
                        }
                    };
                }

            } catch (err) {
                console.error(err);
                alert('Error connecting to tracking server.');
            } finally {
                // Return to normal
                trackBtn.disabled = false;
                trackBtn.style.cursor = '';
                trackBtn.style.opacity = '';
                trackBtn.innerHTML = 'TRACK';
            }
        });
    }
});
