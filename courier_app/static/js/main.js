document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('mainNav');

    let shipmentMap = null;
    let marker = null;
    let destMarker = null;
    let pollingInterval = null;

    function renderMap(lat, lng, dLat, dLng, markerColor) {
        try {
            // Null safety fallback for newly created admin shipments
            const safeLat = lat || 40.7128;
            const safeLng = lng || -74.0060;
            const safeDLat = dLat || 34.0522;
            const safeDLng = dLng || -118.2437;
            
            if (!shipmentMap) {
                shipmentMap = L.map('shipmentMap').setView([safeLat, safeLng], 5);
                // Upgrade to sleek CartoDB Dark Matter tiles for a premium aesthetic
                L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                    maxZoom: 19,
                    attribution: '&copy; OpenStreetMap'
                }).addTo(shipmentMap);
        } else {
            if (marker) shipmentMap.removeLayer(marker);
            if (destMarker) shipmentMap.removeLayer(destMarker);
            
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

        // Sender Location Pin
        var customIcon = L.divIcon({
            html: `<div class="pulse-container"><i class="bi bi-geo-alt-fill text-white" style="font-size: 28px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.6));"></i></div>`,
            iconSize: [28, 28],
            className: 'custom-status-marker'
        });
        marker = L.marker([safeLat, safeLng], { icon: customIcon }).addTo(shipmentMap);
        
        // Active Destination Pin ( pulsing ring )
        var dIcon = L.divIcon({
            html: `<div class="pulse-container" style="position: relative;">
                    <div style="position: absolute; top:0; left:0; width: 100%; height: 100%; border-radius: 50%; border: 3px solid #4ade80; animation: leaflet-pulse 2s infinite ease-out;"></div>
                    <i class="bi bi-geo-alt-fill text-success" style="font-size: 28px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.6));"></i>
                   </div>`,
            iconSize: [28, 28],
            className: 'custom-status-marker'
        });
        destMarker = L.marker([safeDLat, safeDLng], { icon: dIcon }).addTo(shipmentMap);

        // Plane trailing line
        var latlngs = [[safeLat, safeLng], [safeDLat, safeDLng]];
        L.polyline(latlngs, { color: '#e63946', dashArray: '5, 10', weight: 4, opacity: 0.8 }).addTo(shipmentMap);
        shipmentMap.fitBounds(latlngs, { padding: [50, 50] });
        } catch (e) {
            console.error("Map rendering disabled: ", e);
        }
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

                const trackingError = document.getElementById('trackingError');
                // Hide the input bar when results appear
                const trackInputWrapper = trackingInput ? trackingInput.closest('.bg-white.rounded-pill, .p-3.rounded-pill, div') : null;
                // Find the parent container of the input (the pill wrapper)
                const inputBar = trackBtn.closest('.bg-white') || trackBtn.parentElement;

                if (data.success) {
                    if (trackingError) trackingError.classList.add('d-none');
                    if (inputBar) inputBar.style.display = 'none';
                    trackingResult.classList.remove('d-none');

                    // Generate Barcode dynamically (with a tiny delay to ensure DOM is ready)
                    setTimeout(() => {
                        if (window.JsBarcode && document.getElementById('barcode')) {
                            console.log("Initializing Barcode for:", data.tracking_number);
                            JsBarcode("#barcode", data.tracking_number, {
                                format: "CODE128",
                                lineColor: "#212529",
                                width: 2,
                                height: 60,
                                displayValue: true,
                                fontSize: 14,
                                fontOptions: "bold",
                                margin: 10
                            });
                        } else {
                            console.error("JsBarcode library or #barcode SVG missing!");
                        }
                    }, 100);

                    const setElText = (id, text) => {
                        const el = document.getElementById(id);
                        if (el) el.innerText = text;
                    };

                    setElText('resTrackingNumTitle', data.tracking_number);
                    setElText('resStatus', data.status.toUpperCase());
                    setElText('resEstDelivery', data.estimated_delivery);
                    setElText('resOrigin', data.origin);
                    setElText('resDest', data.destination);
                    setElText('resUpdate', data.latest_update);
                    
                    let statusBadgeClass = 'bg-yellow text-dark';
                    if (data.marker_color === 'green') statusBadgeClass = 'bg-success text-white';
                    if (data.marker_color === 'red') statusBadgeClass = 'bg-danger text-white';
                    const statusEl = document.getElementById('resStatus');
                    if (statusEl) statusEl.className = `badge ${statusBadgeClass} px-4 py-2 fs-6 tracking-wide shadow-sm`;

                    // Advanced Fields binding
                    setElText('resAWB', data.airway_bill);
                    setElText('resCreated', data.created_at);
                    setElText('resContent', data.content);
                    setElText('resWeight', data.weight_kg);
                    setElText('resCost', data.shipping_cost);
                    setElText('resSenderName', data.sender_name);
                    setElText('resSenderAddr', data.sender_address);
                    setElText('resReceiverName', data.receiver_name);
                    setElText('resReceiverAddr', data.receiver_address);
                    
                    setElText('resSenderNameSide', data.sender_name);
                    setElText('resSenderAddrSide', data.sender_address);
                    setElText('resReceiverNameSide', data.receiver_name);
                    setElText('resReceiverAddrSide', data.receiver_address);

                    // Timeline logic (Dynamic History)
                    const container = document.getElementById('timelineContainer');
                    if (container) {
                        container.innerHTML = ''; // Clear out any existing nodes
                        
                        if (data.history && data.history.length > 0) {
                            const lastIdx = data.history.length - 1;
                            
                            data.history.forEach((event, idx) => {
                                // Timeline logic (Dynamic History)
                                const isCurrent = (idx === lastIdx);
                                const isPast = (idx < lastIdx);
                                const isEntry = (idx === 0);
                                
                                let iconWrapperClasses = 'tl-icon-wrapper me-2 position-relative';
                                let iconClasses = 'tl-icon fs-5 bi';
                                let rowClasses = 'row align-items-center mb-0 px-2 py-3 d-flex'; // Reduced margin to make line continuous
                                
                                // Add vertical line to all but the last icon
                                if (idx < lastIdx) {
                                    iconWrapperClasses += ' tl-line';
                                }
                                
                                if (isCurrent) {
                                    iconWrapperClasses += ' text-primary';
                                    iconClasses += ' bi-record-circle-fill animate-pulse';
                                    rowClasses += ' bg-light rounded-3 shadow-sm';
                                } else if (isPast) {
                                    iconWrapperClasses += ' text-success';
                                    iconClasses += ' bi-check-circle-fill';
                                }
                                
                                const nodeHtml = `
                                    <div class="${rowClasses}" style="min-height: 80px;">
                                        <div class="col-4 d-flex align-items-center">
                                            <div class="${iconWrapperClasses}" style="width: 24px; z-index: 2;">
                                                <i class="${iconClasses}" style="background: white; border-radius: 50%;"></i>
                                            </div>
                                            <div class="d-flex flex-column">
                                                <h6 class="fw-bold mb-0 tl-title ${isCurrent || isPast ? 'text-dark' : 'text-secondary'}">${event.status}</h6>
                                                <small class="text-muted d-block" style="font-size: 0.70rem;">${event.time}</small>
                                            </div>
                                        </div>
                                        <div class="col-4 text-secondary fs-6 fw-medium">${event.location}</div>
                                        <div class="col-4 text-muted fs-6 small">${event.description}</div>
                                    </div>
                                `;
                                container.insertAdjacentHTML('beforeend', nodeHtml);
                            });
                        } else {
                            container.innerHTML = '<div class="text-center text-muted py-4">No tracking history available yet.</div>';
                        }
                    }
                    if (document.getElementById('shipmentMap')) {
                        renderMap(data.current_lat, data.current_lng, data.dest_lat, data.dest_lng, data.marker_color);
                        
                        // Hide outdated simulation labels completely
                        if(document.getElementById('resAvgSpeed')) document.getElementById('resAvgSpeed').parentElement.style.display = 'none';
                        if(document.getElementById('resEtaHours')) document.getElementById('resEtaHours').parentElement.style.display = 'none';

                        // fix map bounds after visibility change expands the container height
                        setTimeout(() => { if (shipmentMap) shipmentMap.invalidateSize(); }, 300);
                    }
                } else {
                    trackingResult.classList.add('d-none');
                    if (trackingError) {
                        trackingError.classList.remove('d-none');
                        document.getElementById('errorMsg').innerText = data.message || "The tracking number you entered could not be located in our network.";
                    }
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
