import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../services/ml_service.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';
import '../widgets/scan_viewer.dart';
import '../widgets/stats_panel.dart';
import '../widgets/status_indicator.dart';
import 'nii_viewer_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  File? _selectedImage;
  SegmentationResult? _segmentationResult;
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
           
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => NiiViewerScreen(
                slices: slices, 
                fileName: platformFile.name
              ),
            ),
          );
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

    final result = await mlService.runInference(_selectedImage!);
    if (result != null) {
      setState(() => _segmentationResult = result);
    }
  }

  void _clearAll() {
    setState(() {
      _selectedImage = null;
      _segmentationResult = null;
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
          // Logo & Title
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
          // Settings button (especially useful for Android)
          IconButton(
            onPressed: _showServerSettings,
            icon: const Icon(Icons.settings, color: AppTheme.textSecondary),
            tooltip: 'Server Settings',
          ),
          const SizedBox(width: 8),
          // Status Badge
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
          // Left Panel - Controls & Stats (scrollable)
          SizedBox(
            width: 320,
            child: SingleChildScrollView(
              child: _buildControlPanel(mlService),
            ),
          ),
          const SizedBox(width: 24),
          // Right Panel - Image Viewer
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
        // Upload Section
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
                  label: const Text('Browse Files'),
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
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.image,
                        color: AppTheme.accentTeal, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _selectedImage!.path.split(Platform.pathSeparator).last,
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
                ),
              ],
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Analyze Button
        GlassCard(
          gradient: _selectedImage != null && !mlService.isProcessing
              ? AppTheme.primaryGradient
              : null,
          child: InkWell(
            onTap: _selectedImage != null && !mlService.isProcessing
                ? _runAnalysis
                : null,
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
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: _selectedImage != null
                          ? Colors.white
                          : AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Results Panel
        if (_segmentationResult != null)
          StatsPanel(result: _segmentationResult!),

        // View Options
        if (_segmentationResult != null) ...[
          const SizedBox(height: 16),
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Display Options',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildToggleButton(
                        'Original',
                        Icons.image_outlined,
                        !_showOverlay,
                        () => setState(() => _showOverlay = false),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildToggleButton(
                        'Overlay',
                        Icons.layers,
                        _showOverlay,
                        () => setState(() => _showOverlay = true),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildToggleButton(
    String label,
    IconData icon,
    bool isActive,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 12),
        decoration: BoxDecoration(
          color: isActive
              ? AppTheme.primaryBlue.withOpacity(0.2)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isActive ? AppTheme.primaryBlue : AppTheme.surfaceCardHover,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon,
              size: 16,
              color: isActive ? AppTheme.primaryBlue : AppTheme.textSecondary,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: isActive ? AppTheme.primaryBlue : AppTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildViewerPanel(MLService mlService) {
    return GlassCard(
      padding: const EdgeInsets.all(0),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: _selectedImage == null
            ? _buildEmptyViewer()
            : ScanViewer(
                imageFile: _selectedImage!,
                segmentationResult: _segmentationResult,
                showOverlay: _showOverlay,
              ),
      ),
    );
  }

  Widget _buildEmptyViewer() {
    return Container(
      height: 500,
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedBuilder(
              animation: _pulseController,
              builder: (context, child) {
                return Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppTheme.primaryBlue.withOpacity(
                        0.3 + (_pulseController.value * 0.3),
                      ),
                      width: 2,
                    ),
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppTheme.surfaceCard,
                    ),
                    child: Icon(
                      Icons.medical_information_outlined,
                      size: 48,
                      color: AppTheme.primaryBlue.withOpacity(0.7),
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
            const Text(
              'No Scan Loaded',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Upload a CT scan image to begin analysis',
              style: TextStyle(
                fontSize: 14,
                color: AppTheme.textSecondary,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _pickImage,
              icon: const Icon(Icons.add),
              label: const Text('Select Image'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
