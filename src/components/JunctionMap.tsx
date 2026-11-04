'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  JunctionNode,
  TrackedUser,
  CorridorStatus,
  Direction,
  SignalPhase,
} from '../types/traffic';
import { MapPin, Navigation, Compass, AlertOctagon, ShieldCheck, Zap } from 'lucide-react';

interface JunctionMapProps {
  junction: JunctionNode;
  users: TrackedUser[];
  corridors: Record<Direction, CorridorStatus>;
  selectedUser: TrackedUser | null;
  onSelectUser: (user: TrackedUser | null) => void;
  onAddUserAtCoords: (lat: number, lng: number) => void;
  currentPhase: SignalPhase;
}

export const JunctionMap: React.FC<JunctionMapProps> = ({
  junction,
  users,
  corridors,
  selectedUser,
  onSelectUser,
  onAddUserAtCoords,
  currentPhase,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersLayerRef = useRef<any>(null);
  const zonesLayerRef = useRef<any>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize Leaflet Map
  useEffect(() => {
    let isMounted = true;

    if (!mapContainerRef.current) return;

    import('leaflet').then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
      }

      const map = L.map(mapContainerRef.current, {
        center: [junction.lat, junction.lng],
        zoom: 16,
        zoomControl: false,
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // OpenStreetMap standard tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      // Layers for zones and markers
      const zonesLayer = L.layerGroup().addTo(map);
      const markersLayer = L.layerGroup().addTo(map);

      zonesLayerRef.current = zonesLayer;
      markersLayerRef.current = markersLayer;
      mapInstanceRef.current = map;

      // Handle map click to drop simulated commuters
      map.on('click', (e: any) => {
        onAddUserAtCoords(e.latlng.lat, e.latlng.lng);
      });

      setMapLoaded(true);
    });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [junction.id]);

  // Update map center when junction changes
  useEffect(() => {
    if (mapInstanceRef.current && mapLoaded) {
      mapInstanceRef.current.setView([junction.lat, junction.lng], 16);
    }
  }, [junction.lat, junction.lng, mapLoaded]);

  // Render Geofence zones, corridors, and user markers
  useEffect(() => {
    if (!mapLoaded || !mapInstanceRef.current) return;

    import('leaflet').then((L) => {
      const map = mapInstanceRef.current;
      const zonesLayer = zonesLayerRef.current;
      const markersLayer = markersLayerRef.current;

      if (!zonesLayer || !markersLayer) return;

      zonesLayer.clearLayers();
      markersLayer.clearLayers();

      // 1. Geofence Radius Circles (500m outer, 300m mid, 150m inner)
      const outerCircle = L.circle([junction.lat, junction.lng], {
        radius: junction.geofenceRadiusMeters,
        color: '#6366f1',
        weight: 1.5,
        dashArray: '6, 6',
        fillColor: '#6366f1',
        fillOpacity: 0.04,
      }).addTo(zonesLayer);

      const midCircle = L.circle([junction.lat, junction.lng], {
        radius: 300,
        color: '#818cf8',
        weight: 1,
        dashArray: '4, 4',
        fillColor: '#818cf8',
        fillOpacity: 0.05,
      }).addTo(zonesLayer);

      const innerCircle = L.circle([junction.lat, junction.lng], {
        radius: 150,
        color: '#10b981',
        weight: 1.5,
        fillColor: '#10b981',
        fillOpacity: 0.08,
      }).addTo(zonesLayer);

      // 2. Junction Center Marker
      const isNSGreen = currentPhase.includes('NORTH_SOUTH');
      const junctionHtml = `
        <div class="relative flex items-center justify-center w-10 h-10 rounded-full bg-zinc-950 border-2 ${
          isNSGreen ? 'border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.7)]' : 'border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.7)]'
        }">
          <div class="w-3 h-3 rounded-full ${isNSGreen ? 'bg-emerald-400 animate-ping' : 'bg-indigo-400 animate-pulse'}"></div>
          <div class="absolute -bottom-6 font-mono font-bold text-[10px] text-zinc-100 whitespace-nowrap bg-black/80 px-2 py-0.5 rounded border border-zinc-700">
            ${junction.name}
          </div>
        </div>
      `;

      const junctionIcon = L.divIcon({
        html: junctionHtml,
        className: 'custom-junction-icon',
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      });

      L.marker([junction.lat, junction.lng], { icon: junctionIcon }).addTo(zonesLayer);

      // 3. Render Active User Markers on Map
      users.forEach((user) => {
        const isSelected = selectedUser?.id === user.id;
        const isOvercrowded = corridors[user.corridor]?.congestionLevel === 'OVERCROWDED';

        let markerColor = 'bg-indigo-600 border-indigo-400';
        if (isOvercrowded) {
          markerColor = user.distanceMeters > 150 ? 'bg-red-600 border-red-300' : 'bg-amber-500 border-amber-300';
        }

        const userHtml = `
          <div class="relative flex items-center justify-center w-7 h-7 rounded-full text-white font-mono text-[9px] font-bold border-2 ${markerColor} ${
            isSelected ? 'ring-4 ring-white scale-125 z-50' : 'hover:scale-110'
          } shadow-lg transition-transform">
            <span>${user.id.replace('USR-', '#')}</span>
            ${user.advice.action === 'REROUTE' ? '<span class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full ring-1 ring-white animate-pulse"></span>' : ''}
          </div>
        `;

        const icon = L.divIcon({
          html: userHtml,
          className: 'custom-user-icon',
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        });

        const marker = L.marker([user.lat, user.lng], { icon }).addTo(markersLayer);

        // Marker popup content
        const popupContent = `
          <div class="p-1 max-w-[220px]">
            <div class="flex items-center justify-between border-b border-zinc-700 pb-1 mb-1.5">
              <span class="font-bold text-xs text-white">${user.name}</span>
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300">${user.corridor}</span>
            </div>
            <div class="text-[11px] text-zinc-300 space-y-1">
              <div>Distance to Light: <strong class="text-white">${user.distanceMeters}m</strong></div>
              <div>Current Speed: <strong class="text-white">${user.speedKmh} km/h</strong></div>
              <div class="mt-2 p-1.5 rounded bg-zinc-900 border border-zinc-700">
                <div class="font-bold text-[10px] ${user.advice.severity === 'alert' ? 'text-red-400' : 'text-emerald-400'}">
                  ${user.advice.title}
                </div>
                <div class="text-[10px] text-zinc-400 mt-0.5">${user.advice.message}</div>
                ${user.advice.alternateRouteBenefit ? `<div class="text-[9px] text-amber-300 font-semibold mt-1">💡 ${user.advice.alternateRouteBenefit}</div>` : ''}
              </div>
            </div>
          </div>
        `;

        marker.bindPopup(popupContent);

        marker.on('click', () => {
          onSelectUser(user);
        });
      });
    });
  }, [mapLoaded, junction, users, corridors, selectedUser, currentPhase]);

  return (
    <div className="relative w-full h-[480px] bg-zinc-950 rounded-2xl border-2 border-zinc-800 shadow-2xl overflow-hidden flex flex-col">
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-3 z-[1000] bg-zinc-900/90 backdrop-blur-md border border-zinc-800 px-3.5 py-2 rounded-xl shadow-lg flex items-center gap-3">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
        <div>
          <div className="text-xs font-bold text-zinc-100 flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-indigo-400" />
            <span>{junction.name}</span>
          </div>
          <div className="text-[10px] text-zinc-400">{junction.address}</div>
        </div>
      </div>

      {/* Geofence Legend Overlay */}
      <div className="absolute bottom-3 left-3 z-[1000] bg-zinc-900/90 backdrop-blur-md border border-zinc-800 px-3 py-2 rounded-xl shadow-lg text-[10px] space-y-1 hidden sm:block">
        <div className="font-bold text-zinc-300 uppercase tracking-wider mb-1">Geofence Radius</div>
        <div className="flex items-center gap-2 text-zinc-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>Inner Zone (&lt; 150m): Signal Queue</span>
        </div>
        <div className="flex items-center gap-2 text-zinc-400">
          <span className="w-2 h-2 rounded-full bg-indigo-400" />
          <span>Mid Zone (150m - 300m): Deceleration</span>
        </div>
        <div className="flex items-center gap-2 text-zinc-400">
          <span className="w-2 h-2 rounded-full bg-purple-400" />
          <span>Outer Catchment (300m - 500m): Influx</span>
        </div>
        <div className="text-[9px] text-zinc-500 pt-0.5 border-t border-zinc-800">
          💡 Click anywhere on map to spawn a commuter
        </div>
      </div>

      {/* Leaflet container */}
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

