import 'package:flutter/material.dart';
import '../config/app_config.dart';

class TrafficStatisticsScreen extends StatelessWidget {
  const TrafficStatisticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Traffic Optimization Metrics',
              style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              'Real-time congestion alleviation & green-wave efficiency',
              style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
            ),
            const SizedBox(height: 20),

            // Top Stat Grid
            Row(
              children: [
                Expanded(
                  child: _buildStatCard('Delay Reduction', '-38.5%', 'vs Fixed Timers', AppConfig.signalGreen),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard('Avg Wait Time', '14.2s', 'Baseline: 28.6s', AppConfig.accentCyan),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard('Vehicles Cleared', '148', 'Throughput/hr: 820', Colors.tealAccent),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard('CO2 Prevented', '4.2 kg', '1.8L Idle Fuel', Colors.lightGreenAccent),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Algorithm Explanation Card
            Card(
              color: AppConfig.cardDark,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'How SmartFlow Reduces Traffic',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    const SizedBox(height: 12),
                    _buildFeatureBullet(
                      'Real-Time Density Allocation',
                      'Dynamically scales green duration from 10s to 55s based on actual multi-corridor vehicle volume.',
                    ),
                    _buildFeatureBullet(
                      'Anti-Starvation Fairness Rule',
                      'Guarantees low-traffic side streets receive right-of-way if commuters wait over 60 seconds.',
                    ),
                    _buildFeatureBullet(
                      'Early Clearance Cutoff',
                      'Immediately switches green to yellow if the active queue drains early, preventing empty intersection delays.',
                    ),
                    _buildFeatureBullet(
                      'Emergency Vehicle Preemption',
                      'Instantly grants green waves to ambulances and first responders.',
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, String subtitle, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppConfig.cardDark,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.grey.shade800),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(color: color, fontSize: 24, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
          ),
          const SizedBox(height: 4),
          Text(subtitle, style: TextStyle(color: Colors.grey.shade500, fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildFeatureBullet(String title, String desc) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline, color: AppConfig.accentCyan, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(height: 2),
                Text(desc, style: TextStyle(color: Colors.grey.shade400, fontSize: 11, height: 1.3)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

