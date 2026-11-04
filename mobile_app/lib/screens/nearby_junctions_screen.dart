import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../providers/junction_provider.dart';

class NearbyJunctionsScreen extends StatelessWidget {
  const NearbyJunctionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final juncProvider = Provider.of<JunctionProvider>(context);
    final junctions = juncProvider.nearbyJunctions;

    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      appBar: AppBar(
        title: const Text('Nearby Road Junctions'),
        backgroundColor: AppConfig.cardDark,
        elevation: 0,
      ),
      body: junctions.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.location_searching, size: 48, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text('Scanning for nearby registered junctions...', style: TextStyle(color: Colors.grey.shade400)),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () => juncProvider.fetchLocationAndJunctions(),
                    style: ElevatedButton.styleFrom(backgroundColor: AppConfig.accentCyan, foregroundColor: AppConfig.primaryDark),
                    child: const Text('Refresh Scan'),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: junctions.length,
              itemBuilder: (context, idx) {
                final j = junctions[idx];
                final isSelected = juncProvider.selectedJunction?.id == j.id;

                return Card(
                  color: isSelected ? AppConfig.cardDark.withBlue(60) : AppConfig.cardDark,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(color: isSelected ? AppConfig.accentCyan : Colors.transparent),
                  ),
                  margin: const EdgeInsets.bottom(12),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: Colors.cyan.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Center(child: Text('🚦', style: TextStyle(fontSize: 22))),
                    ),
                    title: Text(j.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Text(j.address, style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.black38,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text('${j.detectionRadiusMeters}m Geofence', style: const TextStyle(color: Colors.grey, fontSize: 10)),
                            ),
                            if (j.distanceToUserMeters != null) ...[
                              const SizedBox(width: 8),
                              Text('${j.distanceToUserMeters!.toStringAsFixed(0)}m away', style: const TextStyle(color: AppConfig.accentCyan, fontSize: 11)),
                            ],
                          ],
                        ),
                      ],
                    ),
                    trailing: isSelected
                        ? const Icon(Icons.check_circle, color: AppConfig.accentCyan)
                        : const Icon(Icons.chevron_right, color: Colors.grey),
                    onTap: () {
                      juncProvider.selectJunction(j);
                      Navigator.pop(context);
                    },
                  ),
                );
              },
            ),
    );
  }
}

