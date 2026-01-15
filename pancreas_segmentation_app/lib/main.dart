import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen_web.dart';
import 'screens/nii_scan_screen.dart';
import 'services/ml_service.dart';
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
        ChangeNotifierProvider(create: (_) => MLService()),
        ChangeNotifierProvider(create: (_) => NiiService()),
      ],
      child: MaterialApp(
        title: 'CT Scan Analyzer',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.dark,
        home: const MainNavigator(),
      ),
    );
  }
}

class MainNavigator extends StatefulWidget {
  const MainNavigator({super.key});

  @override
  State<MainNavigator> createState() => _MainNavigatorState();
}

class _MainNavigatorState extends State<MainNavigator> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const HomeScreenWeb(),
    const NiiScanScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            backgroundColor: AppTheme.surfaceCard,
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) {
              setState(() {
                _selectedIndex = index;
              });
            },
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.image),
                label: Text('Single Image'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.analytics),
                label: Text('NIfTI Scan'),
              ),
            ],
          ),
          Expanded(
            child: _screens[_selectedIndex],
          ),
        ],
      ),
    );
  }
}
