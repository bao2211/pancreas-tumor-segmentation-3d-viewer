import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen_web.dart';
import 'services/ml_service.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PancreasSegmentationApp());
}

class PancreasSegmentationApp extends StatelessWidget {
  const PancreasSegmentationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MLService(),
      child: MaterialApp(
        title: 'CT Scan Analyzer',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.dark,
        home: const HomeScreenWeb(),
      ),
    );
  }
}
