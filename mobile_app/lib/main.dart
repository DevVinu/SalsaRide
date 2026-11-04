import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/app_config.dart';
import 'providers/auth_provider.dart';
import 'providers/junction_provider.dart';
import 'providers/signal_provider.dart';
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const SmartFlowApp());
}

class SmartFlowApp extends StatelessWidget {
  const SmartFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => JunctionProvider()),
        ChangeNotifierProvider(create: (_) => SignalProvider()),
      ],
      child: MaterialApp(
        title: AppConfig.appName,
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          brightness: Brightness.dark,
          scaffoldBackgroundColor: AppConfig.primaryDark,
          colorScheme: const ColorScheme.dark(
            primary: AppConfig.accentCyan,
            secondary: AppConfig.signalGreen,
            surface: AppConfig.cardDark,
          ),
          fontFamily: 'sans-serif',
        ),
        home: const SplashScreen(),
      ),
    );
  }
}

