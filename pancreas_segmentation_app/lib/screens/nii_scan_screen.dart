import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import '../services/nii_service.dart';
import '../models/nii_scan.dart';
import '../theme/app_theme.dart';
import '../widgets/model_info_card.dart';
import '../widgets/scan_statistics_panel.dart';
import '../widgets/volume_3d_viewer.dart';

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

  Future<void> _open3DViewer() async {
    final service = context.read<NiiService>();
    
    // Show loading dialog
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => Container(
        color: Colors.black.withValues(alpha: 0.7),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(color: AppTheme.primaryBlue),
              SizedBox(height: 16),
              Text(
                'Generating 3D visualization...',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 16,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Processing volume data and meshes...',
                style: TextStyle(
                  color: AppTheme.textSecondary,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
    
    // Generate volume viewer data (includes volume and meshes)
    final volumeViewerData = await service.generateVolumeViewer();
    
    print('Received volumeViewerData from service: ${volumeViewerData != null ? "YES" : "NO"}');
    if (volumeViewerData != null) {
      print('Volume dimensions: ${volumeViewerData['dimensions']}');
      print('Model URL: ${volumeViewerData['modelUrl'] != null ? "YES" : "NO"}');
    }
    
    if (!mounted) return;
    Navigator.pop(context); // Close loading dialog
    
    if (volumeViewerData != null && volumeViewerData['modelUrl'] != null) {
      print('Opening Volume3DViewer dialog with volume rendering...');
      // Show 3D viewer in fullscreen dialog
      showDialog(
        context: context,
        builder: (context) {
          print('Building Volume3DViewer with volume data');
          return Volume3DViewer(
            gltfData: volumeViewerData['modelUrl'] as String,
            volumeData: volumeViewerData,
            onClose: () => Navigator.pop(context),
          );
        },
      );
    } else {
      _showSnackBar('Failed to generate 3D visualization', isError: true);
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
    
    return Container(
      decoration: BoxDecoration(
        image: DecorationImage(
          image: const AssetImage('assets/images/hexagonal_background.jpeg'),
          fit: BoxFit.cover,
          colorFilter: ColorFilter.mode(
            const Color(0xFF0F172A).withValues(alpha: 0.85),
            BlendMode.darken,
          ),
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              const Color(0xFF0F172A).withValues(alpha: 0.6),
              const Color(0xFF1E293B).withValues(alpha: 0.8),
              const Color(0xFF0F172A).withValues(alpha: 0.9),
            ],
            stops: const [0.0, 0.5, 1.0],
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 600),
              child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Icon with gradient background
                Container(
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF06B6D4).withValues(alpha: 0.2),
                        const Color(0xFF3B82F6).withValues(alpha: 0.2),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(
                      color: const Color(0xFF06B6D4).withValues(alpha: 0.3),
                      width: 2,
                    ),
                  ),
                  child: const Icon(
                    Icons.cloud_upload_outlined,
                    size: 80,
                    color: Color(0xFF06B6D4),
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Title
                const Text(
                  'Medical Image Analysis',
                  style: TextStyle(
                    fontSize: 32,
                    color: Color(0xFFE2E8F0),
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.5,
                  ),
                ),
                
                const SizedBox(height: 12),
                
                // Subtitle
                const Text(
                  'Upload a NIfTI CT scan for AI-powered pancreas and tumor detection',
                  style: TextStyle(
                    fontSize: 15,
                    color: Color(0xFF94A3B8),
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                const SizedBox(height: 48),
                
                // Server selection card
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: const Color(0xFF334155),
                      width: 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: const Color(0xFF06B6D4).withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(
                              Icons.dns_outlined,
                              color: Color(0xFF06B6D4),
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          const Text(
                            'SERVER CONFIGURATION',
                            style: TextStyle(
                              color: Color(0xFFE2E8F0),
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1,
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 20),
                      
                      // Server dropdown
                      Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: service.isServerReady
                                ? const Color(0xFF06B6D4).withValues(alpha: 0.5)
                                : const Color(0xFF334155),
                            width: 1.5,
                          ),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: service.serverUrl,
                            isExpanded: true,
                            dropdownColor: const Color(0xFF1E293B),
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                            icon: const Icon(Icons.arrow_drop_down, color: Color(0xFF06B6D4)),
                            style: const TextStyle(
                              color: Color(0xFFE2E8F0),
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                            ),
                            items: [
                              ...NiiService.serverOptions.map((server) => DropdownMenuItem(
                                value: server['url'],
                                child: Row(
                                  children: [
                                    Icon(
                                      Icons.circle,
                                      size: 8,
                                      color: service.serverUrl == server['url'] && service.isServerReady
                                          ? const Color(0xFF10B981)
                                          : const Color(0xFF64748B),
                                    ),
                                    const SizedBox(width: 12),
                                    Text(server['name']!),
                                    const SizedBox(width: 8),
                                    Text(
                                      '(${server['url']})',
                                      style: const TextStyle(
                                        color: Color(0xFF64748B),
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              )),
                              const DropdownMenuItem(
                                value: 'custom',
                                child: Row(
                                  children: [
                                    Icon(Icons.edit, size: 16, color: Color(0xFF06B6D4)),
                                    SizedBox(width: 12),
                                    Text('Custom Server...'),
                                  ],
                                ),
                              ),
                            ],
                            onChanged: (value) {
                              if (value == 'custom') {
                                _showServerSettings();
                              } else if (value != null) {
                                service.setServerUrl(value);
                                service.checkServer();
                              }
                            },
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Status indicator
                      Row(
                        children: [
                          Icon(
                            service.isServerReady ? Icons.check_circle : Icons.error_outline,
                            color: service.isServerReady ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                            size: 18,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              service.statusMessage,
                              style: TextStyle(
                                color: service.isServerReady ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                          if (!service.isServerReady)
                            TextButton.icon(
                              onPressed: () => service.checkServer(),
                              icon: const Icon(Icons.refresh, size: 16),
                              label: const Text('Retry'),
                              style: TextButton.styleFrom(
                                foregroundColor: const Color(0xFF06B6D4),
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Upload button
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton.icon(
                    onPressed: service.isServerReady ? _pickNiiFile : null,
                    icon: const Icon(Icons.file_upload, size: 24),
                    label: const Text(
                      'Upload NIfTI File',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: service.isServerReady
                          ? const Color(0xFF06B6D4)
                          : const Color(0xFF475569),
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: const Color(0xFF334155),
                      disabledForegroundColor: const Color(0xFF64748B),
                      elevation: service.isServerReady ? 4 : 0,
                      shadowColor: const Color(0xFF06B6D4).withValues(alpha: 0.5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // Supported formats
                const Text(
                  'Supported formats: .nii, .nii.gz',
                  style: TextStyle(
                    color: Color(0xFF64748B),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      ),
    );
  }

  Widget _buildScanView(NiiScan scan, NiiService service) {
    return Row(
      children: [
        // Left sidebar - Detection details
        Container(
          width: 380,
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                offset: const Offset(4, 0),
                blurRadius: 20,
              ),
            ],
          ),
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // File Info
                _buildFileInfo(scan),
                const SizedBox(height: 20),
                
                // Scan Controls with progress
                _buildScanControls(scan, service),
                const SizedBox(height: 20),
                
                // Statistics (shown after full scan)
                if (scan.isFullyScanned) ...[
                  ScanStatisticsPanel(scan: scan),
                  const SizedBox(height: 20),
                ],
                
                // Model Information
                const ModelInfoCard(),
              ],
            ),
          ),
        ),
        
        // Main viewer - larger on right
        Expanded(
          flex: 3,
          child: _buildSliceViewer(scan),
        ),
      ],
    );
  }

  Widget _buildFileInfo(NiiScan scan) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFF06B6D4).withValues(alpha: 0.15),
            const Color(0xFF3B82F6).withValues(alpha: 0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF06B6D4).withValues(alpha: 0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF06B6D4).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.medical_information,
                  color: Color(0xFF06B6D4),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'SCAN INFORMATION',
                style: TextStyle(
                  color: Color(0xFFE2E8F0),
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildInfoRow(Icons.insert_drive_file, 'File', scan.fileName, maxLines: 2),
          const SizedBox(height: 12),
          _buildInfoRow(Icons.grid_3x3, 'Dimensions', scan.volumeDimensions),
          const SizedBox(height: 12),
          _buildInfoRow(Icons.layers, 'Total Slices', '${scan.numSlices}'),
          const SizedBox(height: 12),
          _buildInfoRow(
            Icons.check_circle,
            'Analyzed',
            '${scan.numScanned} / ${scan.numSlices}',
            valueColor: scan.isFullyScanned ? const Color(0xFF10B981) : const Color(0xFFF59E0B),
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
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: const Color(0xFF94A3B8)),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label.toUpperCase(),
                style: const TextStyle(
                  fontSize: 10,
                  color: Color(0xFF64748B),
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: TextStyle(
                  fontSize: 13,
                  color: valueColor ?? const Color(0xFFE2E8F0),
                  fontWeight: FontWeight.w600,
                ),
                maxLines: maxLines,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildScanControls(NiiScan scan, NiiService service) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF334155).withValues(alpha: 0.5),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.analytics_outlined, color: Color(0xFF06B6D4), size: 20),
              SizedBox(width: 10),
              Text(
                'ANALYSIS CONTROLS',
                style: TextStyle(
                  color: Color(0xFFE2E8F0),
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Progress bar when scanning
          if (service.isScanning) ...[
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Analyzing slices...',
                      style: TextStyle(
                        color: Color(0xFFCBD5E1),
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      '${(service.scanProgress * 100).toInt()}%',
                      style: const TextStyle(
                        color: Color(0xFF06B6D4),
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: service.scanProgress,
                    backgroundColor: const Color(0xFF334155),
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF06B6D4)),
                    minHeight: 6,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const SizedBox(
                      width: 14,
                      height: 14,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF06B6D4)),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Processing ${scan.numScanned} / ${scan.numSlices} slices',
                      style: const TextStyle(
                        color: Color(0xFF94A3B8),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
          
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: service.isScanning ? null : _runScan,
              icon: Icon(
                service.isScanning ? Icons.hourglass_empty : Icons.radar,
                size: 20,
              ),
              label: Text(
                service.isScanning ? 'Analyzing...' : 'Start Full Scan',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: service.isScanning 
                    ? const Color(0xFF475569) 
                    : const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                elevation: service.isScanning ? 0 : 2,
              ),
            ),
          ),
          
          if (scan.isFullyScanned) ...[
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: service.isLoading ? null : _open3DViewer,
                icon: const Icon(Icons.view_in_ar, size: 20),
                label: const Text(
                  'View in 3D',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF06B6D4),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  elevation: 2,
                ),
              ),
            ),
          ],
          
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () {
                service.clearScan();
                setState(() {
                  _selectedSliceIndex = 0;
                });
              },
              icon: const Icon(Icons.refresh, size: 20),
              label: const Text(
                'Load New Scan',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Color(0xFF64748B)),
                foregroundColor: const Color(0xFFCBD5E1),
                padding: const EdgeInsets.symmetric(vertical: 16),
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
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: const BoxDecoration(
        color: Color(0xFF0F172A),
        border: Border(
          top: BorderSide(color: Color(0xFF334155), width: 1),
        ),
      ),
      child: Row(
        children: [
          // Previous button
          Container(
            decoration: BoxDecoration(
              color: _selectedSliceIndex > 0 
                  ? const Color(0xFF1E293B) 
                  : const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _selectedSliceIndex > 0 
                    ? const Color(0xFF334155) 
                    : const Color(0xFF1E293B),
                width: 1,
              ),
            ),
            child: IconButton(
              icon: const Icon(Icons.arrow_back_ios_rounded, size: 16),
              color: _selectedSliceIndex > 0 
                  ? const Color(0xFF06B6D4) 
                  : const Color(0xFF334155),
              onPressed: _selectedSliceIndex > 0
                  ? () {
                      final newIndex = _selectedSliceIndex - 1;
                      setState(() {
                        _selectedSliceIndex = newIndex;
                      });
                      if (_pageController.hasClients) {
                        _pageController.jumpToPage(newIndex);
                      }
                    }
                  : null,
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Slider section
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'SLICE',
                      style: TextStyle(
                        color: Color(0xFF64748B),
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1,
                      ),
                    ),
                    Text(
                      '${_selectedSliceIndex + 1} / ${scan.numSlices}',
                      style: const TextStyle(
                        color: Color(0xFFE2E8F0),
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                SliderTheme(
                  data: SliderThemeData(
                    activeTrackColor: const Color(0xFF06B6D4),
                    inactiveTrackColor: const Color(0xFF334155),
                    thumbColor: const Color(0xFF06B6D4),
                    overlayColor: const Color(0xFF06B6D4).withValues(alpha: 0.2),
                    thumbShape: const RoundSliderThumbShape(
                      enabledThumbRadius: 8,
                      elevation: 2,
                    ),
                    trackHeight: 4,
                    overlayShape: const RoundSliderOverlayShape(overlayRadius: 16),
                  ),
                  child: Slider(
                    value: _selectedSliceIndex.toDouble(),
                    min: 0,
                    max: (scan.numSlices - 1).toDouble(),
                    divisions: scan.numSlices - 1,
                    onChanged: (value) {
                      final newIndex = value.toInt();
                      if (newIndex != _selectedSliceIndex) {
                        setState(() {
                          _selectedSliceIndex = newIndex;
                        });
                        if (_pageController.hasClients) {
                          _pageController.jumpToPage(newIndex);
                        }
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(width: 16),
          
          // Next button
          Container(
            decoration: BoxDecoration(
              color: _selectedSliceIndex < scan.numSlices - 1 
                  ? const Color(0xFF1E293B) 
                  : const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _selectedSliceIndex < scan.numSlices - 1 
                    ? const Color(0xFF334155) 
                    : const Color(0xFF1E293B),
                width: 1,
              ),
            ),
            child: IconButton(
              icon: const Icon(Icons.arrow_forward_ios_rounded, size: 16),
              color: _selectedSliceIndex < scan.numSlices - 1 
                  ? const Color(0xFF06B6D4) 
                  : const Color(0xFF334155),
              onPressed: _selectedSliceIndex < scan.numSlices - 1
                  ? () {
                      final newIndex = _selectedSliceIndex + 1;
                      setState(() {
                        _selectedSliceIndex = newIndex;
                      });
                      if (_pageController.hasClients) {
                        _pageController.jumpToPage(newIndex);
                      }
                    }
                  : null,
            ),
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
