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
                        'Outer Detection Geofence: 500m',
                        style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
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
        ],
      ),
    );
  }
}

