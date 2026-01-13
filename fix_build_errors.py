import os

# 1. Fix main.dart
print("Fixing main.dart...")
main_content = r'''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
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
        home: const HomeScreen(),
      ),
    );
  }
}
'''
with open(r'C:\Temp\PancreasProject\pancreas_segmentation_app\lib\main.dart', 'w', encoding='utf-8') as f:
    f.write(main_content)

# 2. Fix home_screen.dart
print("Fixing home_screen.dart...")
home_path = r'C:\Temp\PancreasProject\pancreas_segmentation_app\lib\screens\home_screen.dart'
try:
    with open(home_path, 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Replace runInference with runInferenceOnBytes
    if 'mlService.runInference(_selectedImage!)' in home_content:
        home_content = home_content.replace(
            'mlService.runInference(_selectedImage!)', 
            'mlService.runInferenceOnBytes(await _selectedImage!.readAsBytes())'
        )
    
    # Also replace if it was already partly modified or has spaces
    home_content = home_content.replace(
        'final result = await mlService.runInference(_selectedImage!);',
        'final result = await mlService.runInferenceOnBytes(await _selectedImage!.readAsBytes());'
    )

    with open(home_path, 'w', encoding='utf-8') as f:
        f.write(home_content)
except Exception as e:
    print(f'Error updating home_screen.dart: {e}')

# 3. Fix nii_viewer_screen.dart
print("Fixing nii_viewer_screen.dart...")
nii_path = r'C:\Temp\PancreasProject\pancreas_segmentation_app\lib\screens\nii_viewer_screen.dart'
try:
    with open(nii_path, 'r', encoding='utf-8') as f:
        nii_content = f.read()
    
    if 'AppTheme.background' in nii_content:
        nii_content = nii_content.replace('AppTheme.background', 'AppTheme.surfaceDark')
        with open(nii_path, 'w', encoding='utf-8') as f:
            f.write(nii_content)
    else:
        print("AppTheme.background not found in nii_viewer_screen.dart (maybe already fixed?)")

except Exception as e:
    print(f'Error updating nii_viewer_screen.dart: {e}')

print("All fixes applied.")
