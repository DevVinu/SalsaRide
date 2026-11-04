import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/app_config.dart';
import '../providers/auth_provider.dart';
import 'login_screen.dart';

class UserProfileScreen extends StatelessWidget {
  const UserProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;

    return Scaffold(
      backgroundColor: AppConfig.primaryDark,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 10),
            // Avatar
            CircleAvatar(
              radius: 44,
              backgroundColor: AppConfig.accentCyan.withOpacity(0.2),
              child: const Icon(Icons.person, size: 48, color: AppConfig.accentCyan),
            ),
            const SizedBox(height: 14),
            Text(
              user?.fullName ?? 'Driver Participant',
              style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              user?.email ?? 'driver@smartflow.io',
              style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
            ),
            const SizedBox(height: 24),

            // Profile info card
            Card(
              color: AppConfig.cardDark,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Column(
                children: [
                  _buildListTile(Icons.badge_outlined, 'Role', user?.role ?? 'DRIVER'),
                  const Divider(color: Colors.white10, height: 1),
                  _buildListTile(Icons.phone_outlined, 'Phone', user?.phone ?? 'Not set'),
                  const Divider(color: Colors.white10, height: 1),
                  _buildListTile(Icons.location_on_outlined, 'Location Sharing', user?.locationSharingEnabled == true ? 'Active' : 'Disabled'),
                ],
              ),
            ),
            const SizedBox(height: 30),

            // Logout Button
            ElevatedButton.icon(
              onPressed: () {
                auth.logout();
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              },
              icon: const Icon(Icons.logout, size: 18),
              label: const Text('Log Out'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red.withOpacity(0.15),
                foregroundColor: Colors.redAccent,
                side: const BorderSide(color: Colors.redAccent),
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListTile(IconData icon, String title, String value) {
    return ListTile(
      leading: Icon(icon, color: AppConfig.accentCyan, size: 20),
      title: Text(title, style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
      subtitle: Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
    );
  }
}

