import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/nii_scan_screen.dart';
import 'services/nii_service.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const PancreasSegmentationApp());
}

class PancreasSegmentationApp extends StatelessWidget {
  const PancreasSegmentationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => NiiService()),
      ],
      child: MaterialApp(
        title: 'Pancreas Tumor Detection - NIfTI Analyzer',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.dark,
        home: const NiiScanScreen(),
      ),
    );
  }
}
