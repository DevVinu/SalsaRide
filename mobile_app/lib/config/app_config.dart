import 'package:flutter/material.dart';

class AppConfig {
  static const String appName = 'SmartFlow';
  static const String appVersion = '1.0.0';

  // Base endpoints (Default points to localhost / local emulator 10.0.2.2)
  static String apiBaseUrl = 'http://10.0.2.2:8000/api/v1';
  static String wsBaseUrl = 'ws://10.0.2.2:8000/ws';

  // For testing on real physical device or web
  static void setCustomServer(String host, int port) {
    apiBaseUrl = 'http://$host:$port/api/v1';
    wsBaseUrl = 'ws://$host:$port/ws';
  }

  // Safety Disclaimer constant
  static const String safetyDisclaimer = 
      'IMPORTANT SAFETY NOTICE: SmartFlow is an informational virtual traffic advisory system. '
      'Virtual traffic signals displayed in this application are for connected-vehicle research and simulation. '
      'They do NOT replace or override physical road traffic lights. Always obey official street lights and road laws.';

  // Theme Colors
  static const Color primaryDark = Color(0xFF090D16);
  static const Color cardDark = Color(0xFF1E293B);
  static const Color accentCyan = Color(0xFF38BDF8);
  static const Color signalGreen = Color(0xFF10B981);
  static const Color signalYellow = Color(0xFFF59E0B);
  static const Color signalRed = Color(0xFFEF4444);
}

