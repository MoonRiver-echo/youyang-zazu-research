/**
 * map-layer.js — 地图层交互 (Leaflet)
 */

const MapLayer = (function() {
    let map = null;
    let markers = [];
    let dataStore = [];

    function init() {
        const container = document.getElementById('map-container');
        if (!container) return;

        // Default center: China
        map = L.map('map-container', {
            zoomControl: false,
            attributionControl: false
        }).setView([35.0, 105.0], 4);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 18
        }).addTo(map);

        L.control.zoom({ position: 'bottomright' }).addTo(map);
        L.control.attribution({ position: 'bottomleft' }).addTo(map);
    }

    function update(data) {
        dataStore = data;
        clearMarkers();

        const items = data.filter(item => {
            const lat = parseFloat(item.lat !== undefined ? item.lat : item.latitude);
            const lng = parseFloat(item.lng !== undefined ? item.lng : item.longitude);
            return !isNaN(lat) && !isNaN(lng);
        });

        if (items.length === 0) {
            document.getElementById('map-empty').classList.add('visible');
            document.getElementById('map-container').style.display = 'none';
            return;
        }

        document.getElementById('map-empty').classList.remove('visible');
        document.getElementById('map-container').style.display = 'block';

        const bounds = L.latLngBounds();

        items.forEach(item => {
            const lat = parseFloat(item.lat !== undefined ? item.lat : item.latitude);
            const lng = parseFloat(item.lng !== undefined ? item.lng : item.longitude);
            const name = item.name || item.title || '未命名';
            const category = item.category || '未知';
            const description = item.description || '';
            const source = item.source || '';

            const marker = L.circleMarker([lat, lng], {
                radius: 7,
                fillColor: getCategoryColor(category),
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.85
            }).addTo(map);

            const popupHtml = `
                <div class="popup-title">${escapeHtml(name)}</div>
                <div class="popup-category">${escapeHtml(category)}</div>
                ${description ? `<div class="popup-desc">${escapeHtml(truncate(description, 120))}</div>` : ''}
                ${source ? `<div class="popup-source">来源：${escapeHtml(source)}</div>` : ''}
            `;

            marker.bindPopup(popupHtml, {
                className: 'custom-popup',
                maxWidth: 280,
                minWidth: 200
            });

            markers.push(marker);
            bounds.extend([lat, lng]);
        });

        if (items.length > 0) {
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
        }
    }

    function getCategoryColor(category) {
        const colors = {
            '宗教': '#c53d43',
            '神怪': '#3d7a7a',
            '民俗': '#c9a959',
            '地理': '#8b5a2b',
            '物产': '#5a7a9a',
            '仪式': '#7a5a8a',
            'religion': '#c53d43',
            'supernatural': '#3d7a7a',
            'folklore': '#c9a959',
            'geography': '#8b5a2b',
            'products': '#5a7a9a',
            'rituals': '#7a5a8a'
        };
        return colors[category] || '#4a4a4a';
    }

    function clearMarkers() {
        markers.forEach(m => map.removeLayer(m));
        markers = [];
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function truncate(str, len) {
        if (!str) return '';
        return str.length > len ? str.substring(0, len) + '…' : str;
    }

    return { init, update };
})();
