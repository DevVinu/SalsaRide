import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../providers/auth_provider.dart';
import '../providers/junction_provider.dart';
import '../providers/signal_provider.dart';
import 'live_traffic_map_screen.dart';
import 'virtual_signal_screen.dart';
import 'nearby_junctions_screen.dart';
import 'traffic_statistics_screen.dart';
import 'user_profile_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final juncProvider = Provider.of<JunctionProvider>(context, listen: false);
      juncProvider.fetchLocationAndJunctions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final juncProvider = Provider.of<JunctionProvider>(context);
    final signalProvider = Provider.of<SignalProvider>(context);

    // If junction is selected, ensure subscribed to WebSocket
    if (juncProvider.selectedJunction != null) {
      signalProvider.subscribeToJunction(juncProvider.selectedJunction!.id);
    }

    final screens = [
      _buildHomeDashboard(juncProvider, signalProvider),
      const LiveTrafficMapScreen(),
      const VirtualSignalScreen(),
      const TrafficStatisticsScreen(),
      const UserProfileScreen(),
    ];

    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      appBar: AppBar(
        backgroundColor: AppConfig.cardDark,
        elevation: 0,
        title: Row(
          children: [
            const Text('🚦 ', style: TextStyle(fontSize: 20)),
            const Text(
              'SmartFlow',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: signalProvider.isConnected
                    ? AppConfig.signalGreen.withOpacity(0.2)
                    : Colors.red.withOpacity(0.2),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: signalProvider.isConnected ? AppConfig.signalGreen : Colors.red,
                ),
              ),
              child: Text(
                signalProvider.isConnected ? 'LIVE WS' : 'CONNECTING',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: signalProvider.isConnected ? AppConfig.signalGreen : Colors.red,
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        backgroundColor: AppConfig.cardDark,
        selectedItemColor: AppConfig.accentCyan,
        unselectedItemColor: Colors.grey.shade500,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.map_outlined), label: 'Live Map'),
          BottomNavigationBarItem(icon: Icon(Icons.traffic_outlined), label: 'Signal'),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart_outlined), label: 'Stats'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }

  Widget _buildHomeDashboard(JunctionProvider juncProvider, SignalProvider signalProvider) {
    final junction = juncProvider.selectedJunction;
    final pos = juncProvider.currentPosition;
    final signal = signalProvider.signalState;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Safety Notice Card
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.withOpacity(0.08),
              border: Border.all(color: Colors.amber.shade700.withOpacity(0.4)),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.warning_amber_rounded, color: Colors.amber, size: 24),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Virtual signal is informational only. Do not override physical traffic lights.',
                    style: TextStyle(color: Colors.amber.shade200, fontSize: 11),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Current GPS Location Card
          Card(
            color: AppConfig.cardDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.between,
                    children: [
                      Row(
                        children: const [
                          Icon(Icons.my_location, color: AppConfig.accentCyan, size: 18),
                          SizedBox(width: 8),
                          Text(
                            'Current GPS Fix',
                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                        ],
                      ),
                      IconButton(
                        icon: const Icon(Icons.refresh, size: 20, color: Colors.grey),
                        onPressed: () => juncProvider.fetchLocationAndJunctions(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    pos != null
                        ? 'Lat: ${pos.latitude.toStringAsFixed(4)}, Lon: ${pos.longitude.toStringAsFixed(4)} (Speed: ${(pos.speed * 3.6).toStringAsFixed(1)} km/h)'
                        : 'GPS idle. Tap below to start real-time tracking.',
                    style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 38,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: juncProvider.isTrackingGps ? AppConfig.signalGreen : AppConfig.accentCyan,
                        side: BorderSide(
                          color: juncProvider.isTrackingGps ? AppConfig.signalGreen : AppConfig.accentCyan,
                        ),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                      icon: Icon(
                        juncProvider.isTrackingGps ? Icons.sensors : Icons.play_arrow,
                        size: 18,
                      ),
                      label: Text(
                        juncProvider.isTrackingGps ? '● Live GPS Streaming (Active)' : 'Start Real Mobile GPS Stream',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                      onPressed: () {
                        if (juncProvider.isTrackingGps) {
                          juncProvider.stopLiveGpsTracking();
                        } else {
                          juncProvider.startLiveGpsTracking('MOBILE-USER-01');
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Active Approaching Junction Card
          if (junction != null) ...[
            Card(
              color: AppConfig.cardDark,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        Text(
                          junction.name,
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.cyan.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            junction.junctionCode,
                            style: const TextStyle(color: AppConfig.accentCyan, fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(junction.address, style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
                    const SizedBox(height: 16),

                    // Virtual Light Preview
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.4),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.grey.shade800),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Virtual Signal State',
                                style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                signal?.currentPhase.replaceAll('_', ' ') ?? 'NORTH SOUTH GREEN',
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                            decoration: BoxDecoration(
                              color: AppConfig.primaryDark,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: AppConfig.accentCyan.withOpacity(0.4)),
                            ),
                            child: Text(
                              '${signal?.remainingSeconds ?? 24}s',
                              style: const TextStyle(
                                color: AppConfig.accentCyan,
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.bold,
                                fontSize: 18,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 16),

          // Quick Action Navigation Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => setState(() => _currentIndex = 1),
                  icon: const Icon(Icons.map, size: 18),
                  label: const Text('View Live Map'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppConfig.cardDark,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => setState(() => _currentIndex = 2),
                  icon: const Icon(Icons.traffic, size: 18),
                  label: const Text('Signal HUD'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppConfig.accentCyan,
                    foregroundColor: AppConfig.primaryDark,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

