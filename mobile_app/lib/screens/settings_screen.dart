import 'package:flutter/material.dart';
import '../config/app_config.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _shareLocation = true;
  bool _audioAlerts = true;
  final _serverController = TextEditingController(text: '10.0.2.2:8000');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: AppConfig.cardDark,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildSectionHeader('Participation & Privacy'),
          Card(
            color: AppConfig.cardDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Share GPS with SmartFlow', style: TextStyle(color: Colors.white, fontSize: 14)),
                  subtitle: Text(
                    'Anonymously contributes location when approaching junction geofences',
                    style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                  ),
                  value: _shareLocation,
                  activeColor: AppConfig.accentCyan,
                  onChanged: (val) => setState(() => _shareLocation = val),
                ),
                const Divider(color: Colors.white10, height: 1),
                SwitchListTile(
                  title: const Text('Audio Signal Alerts', style: TextStyle(color: Colors.white, fontSize: 14)),
                  subtitle: Text(
                    'Sound chimes when virtual signal transitions to green or advisory',
                    style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                  ),
                  value: _audioAlerts,
                  activeColor: AppConfig.accentCyan,
                  onChanged: (val) => setState(() => _audioAlerts = val),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          _buildSectionHeader('Backend Server Connectivity'),
          Card(
            color: AppConfig.cardDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Server Host & Port', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _serverController,
                    style: const TextStyle(color: Colors.white, fontSize: 13),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: Colors.black26,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                      hintText: 'e.g. 192.168.1.100:8000',
                      hintStyle: TextStyle(color: Colors.grey.shade600),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: () {
                      final parts = _serverController.text.trim().split(':');
                      if (parts.length == 2) {
                        AppConfig.setCustomServer(parts[0], int.tryParse(parts[1]) ?? 8000);
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Server endpoint updated!')),
                        );
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppConfig.accentCyan,
                      foregroundColor: AppConfig.primaryDark,
                    ),
                    child: const Text('Save Server URL'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          _buildSectionHeader('Safety & Legal'),
          Card(
            color: AppConfig.cardDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            child: ListTile(
              leading: const Icon(Icons.gavel_outlined, color: Colors.amber),
              title: const Text('Safety Disclaimers', style: TextStyle(color: Colors.white, fontSize: 14)),
              subtitle: Text('Review official informational advisory notices', style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
              trailing: const Icon(Icons.chevron_right, color: Colors.grey),
              onTap: () {
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    backgroundColor: AppConfig.cardDark,
                    title: const Text('Safety Disclaimer', style: TextStyle(color: Colors.white)),
                    content: const Text(
                      AppConfig.safetyDisclaimer,
                      style: TextStyle(color: Colors.grey, fontSize: 13, height: 1.4),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(ctx),
                        child: const Text('Understood', style: TextStyle(color: AppConfig.accentCyan)),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 40),

          Center(
            child: Text(
              'SmartFlow v${AppConfig.appVersion}\nAI Intelligent Traffic Management System',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey.shade600, fontSize: 11),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title.toUpperCase(),
        style: const TextStyle(color: AppConfig.accentCyan, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.5),
      ),
    );
  }
}

