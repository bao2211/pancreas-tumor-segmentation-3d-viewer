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
  Map<int, SegmentationResult> _niiResults = {};
  int _currentNiiIndex = 0;
  String? _niiFileName;
  
  // Bulk Scan State
  bool _isBulkAnalyzing = false;

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
        Uint8List? bytes = platformFile.bytes;
        
        if (bytes == null && platformFile.path != null) {
             try {
                bytes = File(platformFile.path!).readAsBytesSync();
             } catch (e) {
                print('Error reading file: $e');
             }
        }

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
          _showSnackBar('Preprocessing NIfTI file (HU Windowing)... please wait.');
          
          final slices = await mlService.uploadNiiFile(bytes);

          if (!mounted) return;

          setState(() {
            _niiSlices = slices;
            _niiFileName = platformFile.name;
            _currentNiiIndex = slices.length ~/ 2;
            _niiResults.clear(); // Clear old 3D results
            _isBulkAnalyzing = false;

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
          _niiResults.clear();
          _isBulkAnalyzing = false;
        });
      }
    } catch (e) {
      _showSnackBar('Failed to open file: $e', isError: true);
    }
  }

  Future<void> _runAnalysis() async {
    if (_selectedImage == null) return;
    await _runAnalysisOnBytes(await _selectedImage!.readAsBytes(), isNii: false);
  }

  Future<void> _analyzeAllSlices() async {
    if (_niiSlices == null || _niiSlices!.isEmpty) return;
    
    setState(() => _isBulkAnalyzing = true);
    _showSnackBar("Starting full scan of ${_niiSlices!.length} slices...");

    for (int i = 0; i < _niiSlices!.length; i++) {
        if (!_isBulkAnalyzing || !mounted) break;
        
        // Show progress by updating current slice view
        setState(() => _currentNiiIndex = i);
        
        final sliceData = _niiSlices![i];
        final bytes = base64Decode(sliceData['image']);
        
        await _runAnalysisOnBytes(bytes, isNii: true, sliceIndex: i);
        
        // Yield to UI loop
        await Future.delayed(Duration.zero);
    }
    
    if (mounted) {
        setState(() => _isBulkAnalyzing = false);
        _showSnackBar("Scan complete.");
    }
  }

  Future<void> _runAnalysisOnBytes(Uint8List bytes, {bool isNii = false, int? sliceIndex}) async {
    final mlService = context.read<MLService>();
    if (!mlService.isModelLoaded) {
      _showSnackBar('Server not connected. Check settings.', isError: true);
      return;
    }

    try {
      final result = await mlService.runInferenceOnBytes(bytes);
      if (result != null) {
        setState(() {
          if (isNii && sliceIndex != null) {
            _niiResults[sliceIndex] = result;
          } else {
            _segmentationResult = result;
          }
        });
      }
    } catch (e) {
      // Don't show snackbar for every single error in bulk mode
      if (!_isBulkAnalyzing) {
         _showSnackBar('Analysis failed: $e', isError: true);
      } else {
         debugPrint('Error analyzing slice $sliceIndex: $e');
      }
    }
  }

  void _clearAll() {
    setState(() {
      _selectedImage = null;
      _segmentationResult = null;
      _niiSlices = null;
      _niiFileName = null;
      _niiResults.clear();
      _isBulkAnalyzing = false;
    });
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).clearSnackBars(); // Clear previous messages to avoid backlog
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
        duration: const Duration(seconds: 2),
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
             const Text('Server URL:', style: TextStyle(color: AppTheme.textSecondary)),
             const SizedBox(height: 8),
            TextField(
              controller: _serverUrlController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'http://localhost:8765',
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
            },
            child: const Text('Save'),
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
            child: _buildViewerPanel(mlService, isWide: true),
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
          _buildViewerPanel(mlService, isWide: false),
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
                  onPressed: (_isBulkAnalyzing) ? null : _pickImage,
                  icon: const Icon(Icons.folder_open),
                  label: const Text('2D Image'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                   onPressed: (_isBulkAnalyzing) ? null : _pickNiiFile,
                   icon: const Icon(Icons.layers),
                   label: const Text('3D NIfTI (.nii.gz)'),
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

        if (_selectedImage != null)
          _buildAnalyzeButton(mlService, _runAnalysis, 'Run 2D Analysis'),

        if (_segmentationResult != null && _selectedImage != null)
          StatsPanel(result: _segmentationResult!),

        // Show Current Slice Stats if NIfTI logic has result for this slice
        if (_niiSlices != null && _niiResults.containsKey(_currentIndexClamped))
           StatsPanel(result: _niiResults[_currentIndexClamped]!),
      ],
    );
  }

  Widget _buildAnalyzeButton(MLService mlService, VoidCallback? onPressed, String label) {
    return GlassCard(
        gradient: !mlService.isProcessing ? AppTheme.primaryGradient : null,
        child: InkWell(
          onTap: !mlService.isProcessing ? onPressed : null,
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
                  mlService.isProcessing ? 'Processing...' : label,
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
            onTap: _isBulkAnalyzing ? null : _clearAll,
            child: Icon(Icons.close,
              color: _isBulkAnalyzing ? Colors.grey : AppTheme.textSecondary, size: 18),
          ),
        ],
      ),
    );
  }

  Widget _buildViewerPanel(MLService mlService, {required bool isWide}) {
    return GlassCard(
      child: Container(
        padding: const EdgeInsets.all(16),
        width: double.infinity,
        height: double.infinity,
        constraints: BoxConstraints(minHeight: isWide ? 500 : 400),
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
                if (_segmentationResult != null || (_niiSlices != null && _niiResults.isNotEmpty))
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
              child: _buildSafeViewerContent(mlService),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSafeViewerContent(MLService mlService) {
      if (_niiSlices != null) {
          return _buildNiiViewer(mlService);
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

  Widget _buildNiiViewer(MLService mlService) {
    if (_niiSlices == null || _niiSlices!.isEmpty) return const SizedBox();

    final currentIndex = _currentIndexClamped;
    final currentSlice = _niiSlices![currentIndex];
    final imageBytes = base64Decode(currentSlice['image']);

    // Check if we have a result for this slice
    final hasResult = _niiResults.containsKey(currentIndex);
    final result = hasResult ? _niiResults[currentIndex] : null;

    return Column(
        children: [
          Expanded(
            child: InteractiveViewer(
                minScale: 0.5,
                maxScale: 4.0,
                child: Center(
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                       Image.memory(
                          imageBytes,
                          fit: BoxFit.contain,
                          gaplessPlayback: true,
                          filterQuality: FilterQuality.high,
                        ),
                        if (_showOverlay && hasResult && result?.overlayBytes != null)
                           Image.memory(
                             result!.overlayBytes!,
                             fit: BoxFit.contain,
                             gaplessPlayback: true,
                           ),
                    ],
                  ),
                ),
            ),
          ),
          const SizedBox(height: 16),

          // NIfTI specific controls
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
                 Text("Slice $_currentNiiIndex", style: const TextStyle(color: Colors.white)),
                 Text("Total: ${_niiSlices!.length}", style: const TextStyle(color: AppTheme.textSecondary)),
            ],
          ),

          Slider(
            value: currentIndex.toDouble(),
            min: 0,
            max: (_niiSlices!.length - 1).toDouble(),
            divisions: (_niiSlices!.length - 1) > 0 ? (_niiSlices!.length - 1) : 1,
            onChanged: (value) {
              if (!_isBulkAnalyzing) {
                setState(() {
                    _currentNiiIndex = value.toInt();
                });
              }
            },
            activeColor: AppTheme.primaryBlue,
          ),

          const SizedBox(height: 8),

          SizedBox(
            width: double.infinity,
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: (_isBulkAnalyzing || mlService.isProcessing) ? null : _analyzeAllSlices,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryBlue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                    icon: const Icon(Icons.analytics_outlined),
                    label: Text(_isBulkAnalyzing ? 'Scanning...' : 'Detect Tumor (All Slices)'),
                  ),
                ),
                if (_isBulkAnalyzing) ...[
                  const SizedBox(width: 8),
                  IconButton(
                     onPressed: () => setState(() => _isBulkAnalyzing = false),
                     icon: const Icon(Icons.stop_circle_outlined, color: AppTheme.error),
                     tooltip: 'Stop Analysis',
                  )
                ]
              ],
            ),
          ),
          const SizedBox(height: 4),
          const Text(
              "Preprocessing including HU Windowing applied automatically.",
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 11),
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
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated home_screen.dart successfully.")
except Exception as e:
    print(f"Error: {e}")
