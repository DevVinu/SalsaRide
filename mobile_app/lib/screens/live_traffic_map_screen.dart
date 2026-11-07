import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../providers/junction_provider.dart';
import '../providers/signal_provider.dart';

class LiveTrafficMapScreen extends StatelessWidget {
  const LiveTrafficMapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final juncProvider = Provider.of<JunctionProvider>(context);
    final signalProvider = Provider.of<SignalProvider>(context);
    final junction = juncProvider.selectedJunction;

    final LatLng center = junction != null
        ? LatLng(junction.latitude, junction.longitude)
        : const LatLng(40.7516, -73.9767);

    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      body: Stack(
        children: [
          FlutterMap(
            options: MapOptions(
              initialCenter: center,
              initialZoom: 16.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'io.smartflow.app',
              ),
              CircleLayer(
                circles: [
                  if (junction != null) ...[
                    // Outer Zone (500m)
                    CircleMarker(
                      point: center,
                      radius: 200,
                      useRadiusInMeter: true,
                      color: const Color(0xFF6366F1).withOpacity(0.1),
                      borderColor: const Color(0xFF6366F1),
                      borderStrokeWidth: 1.5,
                    ),
                    // Inner Stop Line Zone (150m)
                    CircleMarker(
                      point: center,
                      radius: 80,
                      useRadiusInMeter: true,
                      color: AppConfig.signalGreen.withOpacity(0.15),
                      borderColor: AppConfig.signalGreen,
                      borderStrokeWidth: 1.5,
                    ),
                  ],
                ],
              ),
              MarkerLayer(
                markers: [
                  // Center Junction Marker
                  Marker(
                    point: center,
                    width: 44,
                    height: 44,
                    child: Container(
                      decoration: BoxDecoration(
                        color: AppConfig.cardDark,
                        shape: BoxShape.circle,
                        border: Border.all(color: AppConfig.accentCyan, width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.cyan.withOpacity(0.5),
                            blurRadius: 10,
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Text('🚦', style: TextStyle(fontSize: 20)),
                      ),
                    ),
                  ),

                  // User Real GPS Location Marker
                  if (juncProvider.currentPosition != null)
                    Marker(
                      point: LatLng(
                        juncProvider.currentPosition!.latitude,
                        juncProvider.currentPosition!.longitude,
                      ),
                      width: 40,
                      height: 40,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.blueAccent,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.blue.withOpacity(0.6),
                              blurRadius: 10,
                              spreadRadius: 2,
                            ),
                          ],
                        ),
                        child: const Icon(Icons.navigation, color: Colors.white, size: 20),
                      ),
                    ),
                ],
              ),
            ],
          ),

          // Floating Top Junction Banner
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppConfig.cardDark.withOpacity(0.95),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.grey.shade800),
                boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 12)],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.between,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        junction?.name ?? 'Live Junction Map',
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      Text(
                        juncProvider.gpsStatusMessage ?? 'Outer Detection Geofence: 500m',
                        style: TextStyle(
                          color: juncProvider.isTrackingGps ? AppConfig.signalGreen : Colors.grey.shade400,
                          fontSize: 11,
                          fontWeight: juncProvider.isTrackingGps ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.black54,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppConfig.accentCyan.withOpacity(0.5)),
                    ),
                    child: Text(
                      '${signalProvider.signalState?.remainingSeconds ?? 24}s',
                      style: const TextStyle(
                        color: AppConfig.accentCyan,
                        fontFamily: 'monospace',
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Floating Bottom GPS Control Bar & Advisory Banner
          Positioned(
            bottom: 24,
            left: 16,
            right: 16,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // In-car Real-Time Advisory if active
                if (juncProvider.currentAdvisory != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppConfig.cardDark.withOpacity(0.95),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: juncProvider.currentAdvisory!['lamp'] == 'GREEN'
                            ? AppConfig.signalGreen
                            : (juncProvider.currentAdvisory!['lamp'] == 'YELLOW'
                                ? AppConfig.signalYellow
                                : AppConfig.signalRed),
                        width: 2,
                      ),
                    ),
                    child: Row(
                      children: [
                        Text(
                          juncProvider.currentAdvisory!['lamp'] == 'GREEN'
                              ? '🟢'
                              : (juncProvider.currentAdvisory!['lamp'] == 'YELLOW' ? '🟡' : '🔴'),
                          style: const TextStyle(fontSize: 24),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'VIRTUAL SIGNAL: ${juncProvider.currentAdvisory!['lamp']}',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                              Text(
                                'Recommended Speed: ${juncProvider.currentAdvisory!['recommended_speed_kmh']} km/h',
                                style: TextStyle(color: Colors.grey.shade300, fontSize: 11),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                // Live GPS Toggle Action Button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: juncProvider.isTrackingGps ? Colors.redAccent : const Color(0xFF0284C7),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: Icon(juncProvider.isTrackingGps ? Icons.stop : Icons.satellite_alt),
                    label: Text(
                      juncProvider.isTrackingGps ? 'Stop Live GPS Stream' : '🛰️ Stream My Real Mobile GPS',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    onPressed: () {
                      if (juncProvider.isTrackingGps) {
                        juncProvider.stopLiveGpsTracking();
                      } else {
                        juncProvider.startLiveGpsTracking('MOBILE-DRIVER-01');
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

