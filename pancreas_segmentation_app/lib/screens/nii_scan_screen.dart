import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../services/nii_service.dart';
import '../models/nii_scan.dart';
import '../theme/app_theme.dart';
import '../widgets/model_info_card.dart';
import '../widgets/scan_statistics_panel.dart';

class NiiScanScreen extends StatefulWidget {
  const NiiScanScreen({super.key});

  @override
  State<NiiScanScreen> createState() => _NiiScanScreenState();
}

class _NiiScanScreenState extends State<NiiScanScreen> {
  int _selectedSliceIndex = 0;
  final PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NiiService>().checkServer();
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  Future<void> _pickNiiFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['nii', 'gz'],
        dialogTitle: 'Select NIfTI CT Scan',
        withData: true,
      );

      if (result != null && result.files.single.bytes != null) {
        if (!mounted) return;
        final service = context.read<NiiService>();
        await service.loadNiiFile(
          result.files.single.bytes!,
          result.files.single.name,
        );
        
        if (!mounted) return;
        if (service.currentScan != null) {
          setState(() {
            _selectedSliceIndex = service.currentScan!.numSlices ~/ 2;
          });
          
          // Wait for the PageView to be built before jumping to page
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (_pageController.hasClients) {
              _pageController.jumpToPage(_selectedSliceIndex);
            }
          });
          
          _showSnackBar('Loaded ${service.currentScan!.numSlices} slices');
        }
      }
    } catch (e) {
      if (mounted) {
        _showSnackBar('Failed to load file: $e', isError: true);
      }
    }
  }

  Future<void> _runScan() async {
    final service = context.read<NiiService>();
    if (service.currentScan == null) {
      _showSnackBar('Please load a NIfTI file first', isError: true);
      return;
    }

    await service.scanAllSlices();
    
    if (service.currentScan!.hasAnyTumor) {
      _showTumorAlert();
    }
  }

  void _showTumorAlert() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surfaceCard,
        title: const Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 32),
            SizedBox(width: 12),
            Text('Tumor Detected', style: TextStyle(color: AppTheme.textPrimary)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '⚠️ PHÁT HIỆN VÙNG NGHI NGỜ KHỐI U TUYẾN TỤY',
              style: TextStyle(
                color: Colors.orange,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Số slice phát hiện u: ${context.read<NiiService>().currentScan!.numWithTumor}',
              style: const TextStyle(color: AppTheme.textPrimary),
            ),
            const SizedBox(height: 8),
            const Text(
              'Khuyến nghị: Bác sĩ nên đánh giá lại trên hình ảnh gốc.',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 8),
            const Text(
              'Kết quả mang tính hỗ trợ, không thay thế chẩn đoán lâm sàng.',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 12, fontStyle: FontStyle.italic),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? AppTheme.error : AppTheme.success,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final service = context.watch<NiiService>();
    final scan = service.currentScan;

    return Scaffold(
      backgroundColor: AppTheme.surfaceDark,
      appBar: AppBar(
        backgroundColor: AppTheme.surfaceCard,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.biotech, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Pancreas Tumor Detection System',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                Text(
                  'AI-Powered NIfTI CT Analysis',
                  style: TextStyle(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showServerSettings(),
            tooltip: 'Server Settings',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // Status bar
          _buildStatusBar(service),
          
          // Main content
          Expanded(
            child: scan == null
                ? _buildEmptyState()
                : _buildScanView(scan, service),
          ),
        ],
      ),
      floatingActionButton: scan == null
          ? FloatingActionButton.extended(
              onPressed: service.isServerReady ? _pickNiiFile : null,
              icon: const Icon(Icons.folder_open),
              label: const Text('Load NIfTI File'),
              backgroundColor: service.isServerReady ? AppTheme.primaryBlue : Colors.grey,
            )
          : null,
    );
  }

  Widget _buildStatusBar(NiiService service) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: AppTheme.surfaceCard,
      child: Row(
        children: [
          Icon(
            service.isServerReady ? Icons.check_circle : Icons.error_outline,
            color: service.isServerReady ? AppTheme.success : AppTheme.error,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              service.statusMessage,
              style: const TextStyle(color: AppTheme.textPrimary),
            ),
          ),
          if (service.isScanning)
            SizedBox(
              width: 100,
              child: LinearProgressIndicator(
                value: service.scanProgress,
                backgroundColor: AppTheme.surfaceDark,
                valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primaryBlue),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    final service = context.watch<NiiService>();
    
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.medical_services_outlined, size: 100, color: AppTheme.textSecondary),
          const SizedBox(height: 24),
          const Text(
            'No CT Scan Loaded',
            style: TextStyle(fontSize: 24, color: AppTheme.textPrimary, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            service.isServerReady
                ? 'Click the button below to load a .nii or .nii.gz file'
                : 'Please start the inference server first',
            style: const TextStyle(color: AppTheme.textSecondary),
            textAlign: TextAlign.center,
          ),
          if (!service.isServerReady) ...[
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => service.checkServer(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry Connection'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildScanView(NiiScan scan, NiiService service) {
    return Row(
      children: [
        // Left panel - Info and Statistics (scrollable)
        Container(
          width: 320,
          color: AppTheme.surfaceCard,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // File Info
                _buildFileInfo(scan),
                const SizedBox(height: 16),
                
                // Scan Controls
                _buildScanControls(scan, service),
                const SizedBox(height: 16),
                
                // Model Information
                const ModelInfoCard(),
                const SizedBox(height: 16),
                
                // Statistics (shown after full scan)
                if (scan.isFullyScanned) ...[
                  ScanStatisticsPanel(scan: scan),
                ],
              ],
            ),
          ),
        ),
        
        // Middle panel - Slice list
        Container(
          width: 250,
          color: AppTheme.surfaceDark,
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                color: AppTheme.surfaceCard,
                child: Row(
                  children: [
                    const Icon(Icons.layers, color: AppTheme.primaryBlue, size: 20),
                    const SizedBox(width: 8),
                    const Text(
                      'Slice Navigator',
                      style: TextStyle(
                        color: AppTheme.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(child: _buildSliceList(scan)),
            ],
          ),
        ),
        
        // Right panel - Slice viewer
        Expanded(
          child: _buildSliceViewer(scan),
        ),
      ],
    );
  }

  Widget _buildFileInfo(NiiScan scan) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryBlue.withValues(alpha: 0.2),
            AppTheme.accentTeal.withValues(alpha: 0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppTheme.primaryBlue.withValues(alpha: 0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryBlue.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.medical_information,
                  color: AppTheme.primaryBlue,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'Scan Information',
                  style: TextStyle(
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildInfoRow(Icons.insert_drive_file, 'File', scan.fileName, maxLines: 2),
          _buildInfoRow(Icons.grid_3x3, 'Dimensions', scan.volumeDimensions),
          _buildInfoRow(Icons.layers, 'Total Slices', '${scan.numSlices}'),
          _buildInfoRow(
            Icons.check_circle,
            'Scanned',
            '${scan.numScanned} / ${scan.numSlices}',
            valueColor: scan.isFullyScanned ? AppTheme.success : AppTheme.warning,
          ),
        ],
      ),
    );
  }
  
  Widget _buildInfoRow(
    IconData icon,
    String label,
    String value, {
    int maxLines = 1,
    Color? valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 14, color: AppTheme.textSecondary),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 10,
                    color: AppTheme.textSecondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 12,
                    color: valueColor ?? AppTheme.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: maxLines,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildScanControls(NiiScan scan, NiiService service) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppTheme.surfaceCardHover,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.play_circle_outline, color: AppTheme.primaryBlue, size: 20),
              SizedBox(width: 8),
              Text(
                'Analysis Controls',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: service.isScanning ? null : _runScan,
              icon: Icon(service.isScanning ? Icons.hourglass_empty : Icons.radar),
              label: Text(service.isScanning ? 'Scanning...' : 'Run Full Scan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryBlue,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                service.clearScan();
                setState(() {
                  _selectedSliceIndex = 0;
                });
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Load New Scan'),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: AppTheme.primaryBlue),
                foregroundColor: AppTheme.primaryBlue,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSliceList(NiiScan scan) {
    return ListView.builder(
      itemCount: scan.numSlices,
      itemBuilder: (context, index) {
        final slice = scan.slices[index];
        final isSelected = index == _selectedSliceIndex;
        
        return ListTile(
          selected: isSelected,
          selectedTileColor: AppTheme.primaryBlue.withValues(alpha: 0.2),
          leading: Icon(
            slice.hasTumor
                ? Icons.warning_amber_rounded
                : slice.hasPancreas
                    ? Icons.check_circle_outline
                    : Icons.circle_outlined,
            color: slice.hasTumor
                ? Colors.orange
                : slice.hasPancreas
                    ? AppTheme.success
                    : AppTheme.textSecondary,
            size: 20,
          ),
          title: Text(
            'Slice ${slice.index}',
            style: TextStyle(
              color: isSelected ? AppTheme.primaryBlue : AppTheme.textPrimary,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          subtitle: slice.isScanned
              ? Text(
                  slice.status,
                  style: const TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 11,
                  ),
                )
              : null,
          onTap: () {
            setState(() {
              _selectedSliceIndex = index;
            });
            if (_pageController.hasClients) {
              _pageController.jumpToPage(index);
            }
          },
        );
      },
    );
  }

  Widget _buildSliceViewer(NiiScan scan) {
    return Column(
      children: [
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            itemCount: scan.numSlices,
            onPageChanged: (index) {
              setState(() {
                _selectedSliceIndex = index;
              });
            },
            itemBuilder: (context, index) {
              final slice = scan.slices[index];
              return _buildSliceImage(slice);
            },
          ),
        ),
        _buildSliceControls(scan),
      ],
    );
  }

  Widget _buildSliceImage(CTSlice slice) {
    final imageToShow = slice.overlayBytes ?? slice.imageBytes;
    
    return Container(
      color: Colors.black,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Expanded(
              child: InteractiveViewer(
                minScale: 0.5,
                maxScale: 4.0,
                child: Image.memory(
                  imageToShow,
                  fit: BoxFit.contain,
                  errorBuilder: (context, error, stackTrace) {
                    return const Center(
                      child: Text(
                        'Error loading image',
                        style: TextStyle(color: Colors.white),
                      ),
                    );
                  },
                ),
              ),
            ),
            if (slice.isScanned)
              Container(
                padding: const EdgeInsets.all(16),
                color: Colors.black.withValues(alpha: 0.7),
                child: Column(
                  children: [
                    Text(
                      'Slice ${slice.index} - ${slice.status}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (slice.hasPancreas) ...[
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            width: 16,
                            height: 16,
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.cyan, width: 2),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Pancreas (${slice.pancreasPixels} pixels)',
                            style: const TextStyle(color: Colors.cyan),
                          ),
                          if (slice.hasTumor) ...[
                            const SizedBox(width: 24),
                            Container(
                              width: 16,
                              height: 16,
                              decoration: BoxDecoration(
                                border: Border.all(color: Colors.red, width: 2),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Tumor (${slice.tumorPixels} pixels)',
                              style: const TextStyle(color: Colors.red),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliceControls(NiiScan scan) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: AppTheme.surfaceCard,
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios),
            onPressed: _selectedSliceIndex > 0
                ? () {
                    setState(() {
                      _selectedSliceIndex--;
                    });
                    if (_pageController.hasClients) {
                      _pageController.animateToPage(
                        _selectedSliceIndex,
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    }
                  }
                : null,
          ),
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Slice ${_selectedSliceIndex + 1} / ${scan.numSlices}',
                  style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.bold),
                ),
                Slider(
                  value: _selectedSliceIndex.toDouble(),
                  min: 0,
                  max: (scan.numSlices - 1).toDouble(),
                  divisions: scan.numSlices - 1,
                  onChanged: (value) {
                    setState(() {
                      _selectedSliceIndex = value.toInt();
                    });
                    if (_pageController.hasClients) {
                      _pageController.jumpToPage(_selectedSliceIndex);
                    }
                  },
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            onPressed: _selectedSliceIndex < scan.numSlices - 1
                ? () {
                    setState(() {
                      _selectedSliceIndex++;
                    });
                    if (_pageController.hasClients) {
                      _pageController.animateToPage(
                        _selectedSliceIndex,
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                      );
                    }
                  }
                : null,
          ),
        ],
      ),
    );
  }

  void _showServerSettings() {
    final service = context.read<NiiService>();
    final controller = TextEditingController(text: service.serverUrl);
    
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
        content: TextField(
          controller: controller,
          style: const TextStyle(color: AppTheme.textPrimary),
          decoration: const InputDecoration(
            labelText: 'Server URL',
            hintText: 'http://localhost:8765',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              service.setServerUrl(controller.text.trim());
              service.checkServer();
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
