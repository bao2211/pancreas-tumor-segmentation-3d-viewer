import os

content = r'''import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../services/ml_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/scan_viewer.dart';
import '../widgets/stats_panel.dart';
import '../widgets/status_indicator.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  // Single 2D Image State
  File? _selectedImage;
  SegmentationResult? _segmentationResult;
  
  // 3D NIfTI State
  List<Map<String, dynamic>>? _niiSlices;
  int _currentNiiIndex = 0;
  String? _niiFileName;

  late AnimationController _pulseController;
  bool _showOverlay = true;
  final TextEditingController _serverUrlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final mlService = context.read<MLService>();
      _serverUrlController.text = mlService.serverUrl;
      mlService.loadModel();
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _serverUrlController.dispose();
    super.dispose();
  }

  Future<void> _pickNiiFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['gz', 'nii'],
        dialogTitle: 'Select CT Scan (.nii.gz)',
        withData: true,
      );

      if (result != null) {
        final platformFile = result.files.single;
        final bytes = platformFile.bytes ?? 
           (platformFile.path != null ? File(platformFile.path!).readAsBytesSync() : null);

        if (bytes == null) {
          _showSnackBar('Could not read file data', isError: true);
          return;
        }

        final mlService = context.read<MLService>();
        if (!mlService.isModelLoaded) {
          _showSnackBar('Server not connected.', isError: true);
          return;
        }

        try {
          final slices = await mlService.uploadNiiFile(bytes);
           
          if (!mounted) return;

          setState(() {
            _niiSlices = slices;
            _niiFileName = platformFile.name;
            _currentNiiIndex = slices.length ~/ 2;
            
            // Clear single image state
            _selectedImage = null;
            _segmentationResult = null;
          });
          
        } catch (e) {
          _showSnackBar('Failed: $e', isError: true);
        }
      }
    } catch (e) {
      _showSnackBar('Failed to pick file: $e', isError: true);
    }
  }

  Future<void> _pickImage() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        dialogTitle: 'Select CT Scan Image',
      );

      if (result != null && result.files.single.path != null) {
        setState(() {
          _selectedImage = File(result.files.single.path!);
          _segmentationResult = null;
          
          // Clear NIfTI state
          _niiSlices = null;
          _niiFileName = null;
        });
      }
    } catch (e) {
      _showSnackBar('Failed to open file: $e', isError: true);
    }
  }

  Future<void> _runAnalysis() async {
    if (_selectedImage == null) return;

    final mlService = context.read<MLService>();
    if (!mlService.isModelLoaded) {
      _showSnackBar('Server not connected. Check settings.', isError: true);
      return;
    }

    try {
      final bytes = await _selectedImage!.readAsBytes();
      final result = await mlService.runInferenceOnBytes(bytes);
      if (result != null) {
        setState(() => _segmentationResult = result);
      }
    } catch (e) {
      _showSnackBar('Analysis failed: $e', isError: true);
    }
  }

  void _clearAll() {
    setState(() {
      _selectedImage = null;
      _segmentationResult = null;
      _niiSlices = null;
      _niiFileName = null;
    });
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: isError ? AppTheme.error : AppTheme.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  void _showServerSettings() {
    final mlService = context.read<MLService>();
    _serverUrlController.text = mlService.serverUrl;
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surfaceCard,
        title: const Row(
          children: [
            Icon(Icons.settings, color: AppTheme.primaryBlue),
            SizedBox(width: 12),
            Text('Server Settings', style: TextStyle(color: AppTheme.textPrimary)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Enter the URL of your inference server.\nFor Android, use your PC\'s IP address (e.g., http://192.168.1.100:8765)',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _serverUrlController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: InputDecoration(
                labelText: 'Server URL',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'http://192.168.1.100:8765',
                hintStyle: TextStyle(color: AppTheme.textSecondary.withOpacity(0.5)),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppTheme.surfaceCardHover),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: const BorderSide(color: AppTheme.primaryBlue),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel', style: TextStyle(color: AppTheme.textSecondary)),
          ),
          ElevatedButton(
            onPressed: () {
              mlService.setServerUrl(_serverUrlController.text.trim());
              mlService.loadModel();
              Navigator.pop(context);
              _showSnackBar('Server URL updated. Reconnecting...');
            },
            child: const Text('Save & Connect'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final mlService = context.watch<MLService>();
    final size = MediaQuery.of(context).size;
    final isWideScreen = size.width > 900;

    return Scaffold(
      backgroundColor: AppTheme.surfaceDark,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(mlService),
            Expanded(
              child: isWideScreen
                  ? _buildWideLayout(mlService)
                  : _buildNarrowLayout(mlService),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(MLService mlService) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.biotech, color: Colors.white, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'CT Scan Analyzer',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                Text(
                  'Pancreas Tumor Segmentation',
                  style: TextStyle(
                    fontSize: 13,
                    color: AppTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: _showServerSettings,
            icon: const Icon(Icons.settings, color: AppTheme.textSecondary),
            tooltip: 'Server Settings',
          ),
          const SizedBox(width: 8),
          StatusIndicator(
            isConnected: mlService.isModelLoaded,
            label: mlService.isModelLoaded ? 'Connected' : 'Offline',
            onRetry: mlService.isModelLoaded ? null : mlService.loadModel,
          ),
        ],
      ),
    );
  }

  Widget _buildWideLayout(MLService mlService) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 320,
            child: SingleChildScrollView(
              child: _buildControlPanel(mlService),
            ),
          ),
          const SizedBox(width: 24),
          Expanded(
            child: _buildViewerPanel(mlService),
          ),
        ],
      ),
    );
  }

  Widget _buildNarrowLayout(MLService mlService) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildViewerPanel(mlService),
          const SizedBox(height: 16),
          _buildControlPanel(mlService),
        ],
      ),
    );
  }

  Widget _buildControlPanel(MLService mlService) {
    return Column(
      children: [
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryBlue.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.upload_file,
                      color: AppTheme.primaryBlue, size: 20),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'Upload Scan',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: _pickImage,
                  icon: const Icon(Icons.folder_open),
                  label: const Text('Browse Image (2D)'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                   onPressed: _pickNiiFile,
                   icon: const Icon(Icons.layers),
                   label: const Text('Load 3D NIfTI (.nii.gz)'),
                   style: OutlinedButton.styleFrom(
                     padding: const EdgeInsets.symmetric(vertical: 16),
                     side: const BorderSide(color: AppTheme.accentTeal),
                     foregroundColor: AppTheme.accentTeal,
                   ),
                ),
              ),
              if (_selectedImage != null) ...[
                const SizedBox(height: 12),
                _buildFileBadge(_selectedImage!.path.split(Platform.pathSeparator).last, Icons.image),
              ],
              if (_niiSlices != null) ...[
                 const SizedBox(height: 12),
                 _buildFileBadge(_niiFileName ?? 'Unknown.nii.gz', Icons.layers),
              ]
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Analyze Button (Only for 2D images for now, Nii is auto-processed on load)
        if (_selectedImage != null)
          GlassCard(
            gradient: !mlService.isProcessing
                ? AppTheme.primaryGradient
                : null,
            child: InkWell(
              onTap: !mlService.isProcessing ? _runAnalysis : null,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (mlService.isProcessing)
                      const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    else
                      const Icon(Icons.auto_awesome, color: Colors.white),
                    const SizedBox(width: 12),
                    Text(
                      mlService.isProcessing ? 'Analyzing...' : 'Run AI Analysis',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        const SizedBox(height: 16),

        if (_segmentationResult != null)
          StatsPanel(result: _segmentationResult!),
      ],
    );
  }

  Widget _buildFileBadge(String fileName, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppTheme.accentTeal, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              fileName,
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.textSecondary,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
          InkWell(
            onTap: _clearAll,
            child: const Icon(Icons.close,
              color: AppTheme.textSecondary, size: 18),
          ),
        ],
      ),
    );
  }

  Widget _buildViewerPanel(MLService mlService) {
    return GlassCard(
      child: Container(
        padding: const EdgeInsets.all(16),
        width: double.infinity,
        height: double.infinity,
        constraints: const BoxConstraints(minHeight: 400),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Scan Viewer',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                // Toggle overlay for 2D result
                if (_segmentationResult != null)
                  Row(
                    children: [
                      Text(
                        'Show Overlay',
                        style: TextStyle(
                          color: AppTheme.textSecondary,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Switch(
                        value: _showOverlay,
                        onChanged: (value) => setState(() => _showOverlay = value),
                        activeColor: AppTheme.primaryBlue,
                      ),
                    ],
                  ),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: _buildSafeViewerContent(),
            ),
          ],
        ),
      ),
    );
  }
  
  // Custom method to handle rendering 2D or 3D viewer, or placeholder
  Widget _buildSafeViewerContent() {
      if (_niiSlices != null) {
          return _buildNiiViewer();
      }
      if (_selectedImage != null) {
          return ScanViewer(
            imageFile: _selectedImage!,
            segmentationResult: _showOverlay ? _segmentationResult : null,
            showOverlay: _showOverlay,
          );
      }
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.image_search, size: 64, color: AppTheme.textSecondary.withOpacity(0.5)),
            const SizedBox(height: 16),
            const Text(
              'No scan selected',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ],
        ),
      );
  }

  Widget _buildNiiViewer() {
    if (_niiSlices == null || _niiSlices!.isEmpty) return const SizedBox();

    final currentSlice = _niiSlices![_currentIndexClamped];
    // Slices are base64 strings
    final imageBytes = base64Decode(currentSlice['image']);

    return Column(
        children: [
          Expanded(
            child: InteractiveViewer(
                minScale: 0.5,
                maxScale: 4.0,
                child: Center(
                  child: Image.memory(
                    imageBytes,
                    fit: BoxFit.contain,
                    gaplessPlayback: true,
                    filterQuality: FilterQuality.high,
                  ),
                ),
            ),
          ),
          const SizedBox(height: 16),
          // NIfTI specific controls
          Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                    Text("Slice $_currentNiiIndex", style: const TextStyle(color: Colors.white)),
                    Text("Total: ${_niiSlices!.length}", style: const TextStyle(color: AppTheme.textSecondary)),
                ],
              ),
              Slider(
                value: _currentIndexClamped.toDouble(),
                min: 0,
                max: (_niiSlices!.length - 1).toDouble(),
                divisions: (_niiSlices!.length - 1) > 0 ? (_niiSlices!.length - 1) : 1,
                onChanged: (value) {
                  setState(() {
                      _currentNiiIndex = value.toInt();
                  });
                },
                activeColor: AppTheme.primaryBlue,
              ),
            ],
          ),
        ],
    );
  }
  
  int get _currentIndexClamped {
    if (_niiSlices == null || _niiSlices!.isEmpty) return 0;
    return _currentNiiIndex.clamp(0, _niiSlices!.length - 1);
  }
}
'''

file_path = r'C:\Temp\PancreasProject\pancreas_segmentation_app\lib\screens\home_screen.dart'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated home_screen.dart successfully.")
