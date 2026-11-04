import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../providers/junction_provider.dart';
import '../providers/signal_provider.dart';

class VirtualSignalScreen extends StatelessWidget {
  const VirtualSignalScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final juncProvider = Provider.of<JunctionProvider>(context);
    final signalProvider = Provider.of<SignalProvider>(context);
    final signal = signalProvider.signalState;
    final advisory = signalProvider.advisory;

    final isNSGreen = signal?.northSouthLamp == 'GREEN';
    final isNSYellow = signal?.northSouthLamp == 'YELLOW';
    final isNSRed = signal?.northSouthLamp == 'RED';

    final isEWGreen = signal?.eastWestLamp == 'GREEN';
    final isEWYellow = signal?.eastWestLamp == 'YELLOW';
    final isEWRed = signal?.eastWestLamp == 'RED';

    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Safety Disclaimer Banner
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.amber.withOpacity(0.08),
                border: Border.all(color: Colors.amber.shade700.withOpacity(0.4)),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.shield_outlined, color: Colors.amber, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Informational virtual signal simulation. Do not override physical street traffic lights.',
                      style: TextStyle(color: Colors.amber.shade200, fontSize: 11),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // 4-Way Traffic Signal Lamp Visualizer Card
            Card(
              color: AppConfig.cardDark,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text(
                      juncProvider.selectedJunction?.name ?? 'Virtual 4-Way Signal',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Dynamic Signal State Machine',
                      style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                    ),
                    const SizedBox(height: 24),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        // North-South Signal Lamp Head
                        _buildSignalHead('NORTH-SOUTH', isNSRed, isNSYellow, isNSGreen, signal?.remainingSeconds ?? 24),

                        // East-West Signal Lamp Head
                        _buildSignalHead('EAST-WEST', isEWRed, isEWYellow, isEWGreen, signal?.remainingSeconds ?? 24),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Priority corridor badge
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.black26,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: Colors.grey.shade800),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.bolt, color: Colors.amber, size: 18),
                          const SizedBox(width: 6),
                          Text(
                            'Priority Allocated Corridor: ${signal?.priorityCorridor ?? 'NORTH'}',
                            style: const TextStyle(color: AppConfig.accentCyan, fontWeight: FontWeight.bold, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // In-Car Driver Guidance & Advisory Card
            Card(
              color: AppConfig.cardDark,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Row(
                          children: const [
                            Icon(Icons.navigation_outlined, color: AppConfig.accentCyan, size: 20),
                            SizedBox(width: 8),
                            Text(
                              'In-Car Driver Advisory',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppConfig.signalGreen.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: AppConfig.signalGreen),
                          ),
                          child: const Text(
                            'PROCEED',
                            style: TextStyle(color: AppConfig.signalGreen, fontSize: 10, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      advisory != null
                          ? advisory.advisoryMessage
                          : 'SalsaRide SmartFlow is monitoring corridor density. Priority green wave assigned to Northbound corridor.',
                      style: TextStyle(color: Colors.grey.shade300, fontSize: 13, height: 1.4),
                    ),
                    const SizedBox(height: 16),

                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.black38,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildMetric('Speed', '32 km/h'),
                          _buildMetric('Distance', '180m'),
                          _buildMetric('Cycle Rem.', '${signal?.remainingSeconds ?? 24}s'),
                        ],
                      ),
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

  Widget _buildMetric(String label, String value) {
    return Column(
      children: [
        Text(label, style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13, fontFamily: 'monospace')),
      ],
    );
  }

  Widget _buildSignalHead(String label, bool isRed, bool isYellow, bool isGreen, int seconds) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        Container(
          width: 80,
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey.shade800, width: 2),
            boxShadow: const [BoxShadow(color: Colors.black54, blurRadius: 10)],
          ),
          child: Column(
            children: [
              _buildLamp(AppConfig.signalRed, isRed),
              const SizedBox(height: 8),
              _buildLamp(AppConfig.signalYellow, isYellow),
              const SizedBox(height: 8),
              _buildLamp(AppConfig.signalGreen, isGreen),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(
          (isGreen || isYellow) ? '${seconds}s' : '--',
          style: const TextStyle(color: AppConfig.accentCyan, fontFamily: 'monospace', fontWeight: FontWeight.bold, fontSize: 16),
        ),
      ],
    );
  }

  Widget _buildLamp(Color color, bool isActive) {
    return Container(
      width: 24,
      height: 24,
      decoration: BoxDecoration(
        color: color.withOpacity(isActive ? 1.0 : 0.2),
        shape: BoxShape.circle,
        boxShadow: isActive ? [BoxShadow(color: color.withOpacity(0.8), blurRadius: 12, spreadRadius: 2)] : null,
      ),
    );
  }
}

