class SmartFlowMap {
  constructor(containerId) {
    this.map = L.map(containerId, { zoomControl: true }).setView([40.7516, -73.9767], 16);
    this.zonesLayer = L.layerGroup().addTo(this.map);
    this.markersLayer = L.layerGroup().addTo(this.map);
    this.currentJunction = null;

    // Standard OpenStreetMap Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.map.on('click', (e) => {
      if (window.onMapClicked) {
        window.onMapClicked(e.latlng.lat, e.latlng.lng);
      }
    });
  }

  setJunction(junction) {
    this.currentJunction = junction;
    this.map.setView([junction.latitude, junction.longitude], 16);
    this.renderGeofenceZones(junction);
  }

  renderGeofenceZones(junction) {
    this.zonesLayer.clearLayers();

    const lat = junction.latitude;
    const lon = junction.longitude;

    // Outer Geofence (500m)
    L.circle([lat, lon], {
      radius: junction.detection_radius_meters || 500,
      color: '#6366f1',
      weight: 1.5,
      dashArray: '6, 6',
      fillColor: '#6366f1',
      fillOpacity: 0.05,
    }).addTo(this.zonesLayer);

    // Mid Deceleration Zone (300m)
    L.circle([lat, lon], {
      radius: junction.mid_zone_meters || 300,
      color: '#a855f7',
      weight: 1.2,
      dashArray: '4, 4',
      fillColor: '#a855f7',
      fillOpacity: 0.06,
    }).addTo(this.zonesLayer);

    // Inner Stop-Line Queue Zone (150m)
    L.circle([lat, lon], {
      radius: junction.inner_zone_meters || 150,
      color: '#10b981',
      weight: 1.5,
      fillColor: '#10b981',
      fillOpacity: 0.09,
    }).addTo(this.zonesLayer);

    // Center Junction Marker
    const junctionHtml = `
      <div style="background: #0f172a; border: 2px solid #38bdf8; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(56, 189, 248, 0.6);">
        <div style="width: 10px; height: 10px; background: #38bdf8; border-radius: 50%;"></div>
      </div>
    `;

    const jIcon = L.divIcon({
      html: junctionHtml,
      className: 'junc-icon',
      iconSize: [34, 34],
      iconAnchor: [17, 17],
    });

    L.marker([lat, lon], { icon: jIcon })
      .bindPopup(`<strong>${junction.name}</strong><br>${junction.address}`)
      .addTo(this.zonesLayer);
  }

  renderParticipants(participants) {
    this.markersLayer.clearLayers();

    if (!participants || !participants.length) return;

    participants.forEach((p) => {
      if (!p.latitude || !p.longitude) return;

      const isSos = p.is_emergency;
      const color = isSos ? '#ef4444' : '#38bdf8';
      const border = isSos ? '#fca5a5' : '#7dd3fc';

      const iconHtml = `
        <div style="background: ${color}; border: 2px solid ${border}; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 10px; font-weight: bold; font-family: monospace; box-shadow: 0 2px 8px rgba(0,0,0,0.4); ${isSos ? 'animation: pulse 1s infinite;' : ''}">
          ${isSos ? '🚨' : '🚗'}
        </div>
      `;

      const markerIcon = L.divIcon({
        html: iconHtml,
        className: 'veh-icon',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
      });

      const marker = L.marker([p.latitude, p.longitude], { icon: markerIcon }).addTo(this.markersLayer);
      marker.bindPopup(`
        <div style="font-size: 11px; padding: 4px;">
          <div><strong>ID:</strong> ${p.vehicle_id || p.user_id}</div>
          <div><strong>Corridor:</strong> ${p.corridor}</div>
          <div><strong>Distance:</strong> ${Math.round(p.distance_meters)}m</div>
          <div><strong>Speed:</strong> ${p.speed_kmh} km/h</div>
          <div><strong>Wait:</strong> ${p.waiting_seconds || 0}s</div>
        </div>
      `);
    });
  }
}

