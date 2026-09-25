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

    if (trackBtn && trackingInput && !document.getElementById('trackingPage')) {
        const homeForm = trackingInput.closest('form');
        if (homeForm) {
            homeForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const code = trackingInput.value.trim();
                if (code) {
                    window.location.href = `/track/?track=${encodeURIComponent(code)}`;
                }
            });
        } else {
            trackBtn.addEventListener('click', () => {
                const code = trackingInput.value.trim();
                if (code) {
                    window.location.href = `/track/?track=${encodeURIComponent(code)}`;
                }
            });
            trackingInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    const code = trackingInput.value.trim();
                    if (code) {
                        window.location.href = `/track/?track=${encodeURIComponent(code)}`;
                    }
                }
            });
        }
    }
});
