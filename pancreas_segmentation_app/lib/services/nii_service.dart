import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/nii_scan.dart';

/// Service for loading and processing NIfTI CT scans
class NiiService extends ChangeNotifier {
  String _serverUrl = 'http://localhost:8765';
  bool _isServerReady = false;
  bool _isLoading = false;
  bool _isScanning = false;
  double _scanProgress = 0.0;
  String _statusMessage = 'Ready';
  
  NiiScan? _currentScan;
  
  bool get isServerReady => _isServerReady;
  bool get isLoading => _isLoading;
  bool get isScanning => _isScanning;
  double get scanProgress => _scanProgress;
  String get statusMessage => _statusMessage;
  NiiScan? get currentScan => _currentScan;
  String get serverUrl => _serverUrl;
  
  void setServerUrl(String url) {
    _serverUrl = url;
    notifyListeners();
  }
  
  /// Check if server is running and models are loaded
  Future<void> checkServer() async {
    try {
      _statusMessage = 'Checking server...';
      notifyListeners();
      
      final response = await http
          .get(Uri.parse('$_serverUrl/health'))
          .timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Server is ready if it responds, models will load on demand
        _isServerReady = data['status'] == 'ok';
        
        if (_isServerReady) {
          if (data['models_loaded'] == true) {
            _statusMessage = 'Server ready - models loaded';
          } else {
            _statusMessage = 'Server ready - models will load on first scan';
          }
        } else {
          _statusMessage = 'Server error';
        }
      } else {
        _isServerReady = false;
        _statusMessage = 'Server not responding';
      }
    } catch (e) {
      _isServerReady = false;
      _statusMessage = 'Server not reachable';
      debugPrint('Server check error: $e');
    }
    notifyListeners();
  }
  
  /// Load a .nii or .nii.gz file
  Future<NiiScan?> loadNiiFile(Uint8List fileBytes, String fileName) async {
    if (!_isServerReady) {
      _statusMessage = 'Server not ready';
      notifyListeners();
      return null;
    }
    
    try {
      _isLoading = true;
      _statusMessage = 'Loading NIfTI file...';
      _currentScan = null;
      notifyListeners();
      
      // Send file to server
      final base64File = base64Encode(fileBytes);
      
      final response = await http.post(
        Uri.parse('$_serverUrl/load_nii'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'file': base64File}),
      ).timeout(const Duration(seconds: 120));
      
      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }
      
      final result = jsonDecode(response.body);
      if (result['success'] != true) {
        throw Exception(result['error'] ?? 'Unknown error');
      }
      
      // Parse slices
      final slicesData = result['slices'] as List;
      final slices = slicesData.map((s) {
        return CTSlice(
          index: s['index'] as int,
          imageBytes: base64Decode(s['image'] as String),
          shape: List<int>.from(s['shape']),
        );
      }).toList();
      
      _currentScan = NiiScan(
        fileName: fileName,
        slices: slices,
        volumeShape: List<int>.from(result['volume_shape']),
      );
      
      _isLoading = false;
      _statusMessage = 'Loaded ${slices.length} slices';
      notifyListeners();
      
      return _currentScan;
      
    } catch (e) {
      _isLoading = false;
      _statusMessage = 'Error loading file: $e';
      debugPrint('Error loading NIfTI: $e');
      notifyListeners();
      return null;
    }
  }
  
  /// Scan all slices with pancreas and tumor models (BATCH MODE - CONTEXT-AWARE)
  Future<void> scanAllSlices({bool useBatchMode = true}) async {
    if (_currentScan == null || !_isServerReady) return;
    
    try {
      _isScanning = true;
      _scanProgress = 0.0;
      notifyListeners();
      
      if (useBatchMode) {
        // Use new batch endpoint for better performance and context-aware processing
        await _scanAllBatch();
      } else {
        // Fallback: scan slices one by one
        await _scanAllSequential();
      }
      
      _isScanning = false;
      _statusMessage = 'Scan complete - Found ${_currentScan!.numWithTumor} slices with tumor';
      notifyListeners();
      
    } catch (e) {
      _isScanning = false;
      _statusMessage = 'Scan error: $e';
      debugPrint('Scan error: $e');
      notifyListeners();
    }
  }
  
  /// Batch scan using server-side context-aware processing
  Future<void> _scanAllBatch() async {
    try {
      _statusMessage = 'Processing all slices (context-aware)...';
      notifyListeners();
      
      final response = await http.post(
        Uri.parse('$_serverUrl/scan_all'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(minutes: 10));  // Longer timeout for batch processing
      
      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }
      
      final result = jsonDecode(response.body);
      if (result['success'] != true) {
        throw Exception(result['error'] ?? 'Unknown error');
      }
      
      // Parse batch results
      final results = result['results'] as List;
      final totalSlices = results.length;
      
      for (var i = 0; i < results.length; i++) {
        final sliceResult = results[i];
        final sliceIndex = sliceResult['slice_index'] as int;
        
        // Find corresponding slice
        final slice = _currentScan!.slices.firstWhere((s) => s.index == sliceIndex);
        
        // Decode overlay
        final overlayBytes = base64Decode(sliceResult['overlay'] as String);
        
        // Update slice with results
        slice.updateResults(
          hasPancreas: sliceResult['has_pancreas'] as bool,
          hasTumor: sliceResult['has_tumor'] as bool,
          pancreasPixels: sliceResult['pancreas_pixels'] as int,
          tumorPixels: sliceResult['tumor_pixels'] as int,
          overlayBytes: overlayBytes,
        );
        
        // Update progress
        _scanProgress = (i + 1) / totalSlices;
        if ((i + 1) % 10 == 0 || i == totalSlices - 1) {
          _statusMessage = 'Processed ${i + 1}/$totalSlices slices (context-aware)';
          notifyListeners();
        }
      }
      
      debugPrint('Batch scan complete: ${result['summary']}');
      
    } catch (e) {
      debugPrint('Batch scan error: $e');
      rethrow;
    }
  }
  
  /// Sequential scan (fallback method)
  Future<void> _scanAllSequential() async {
    final totalSlices = _currentScan!.numSlices;
    
    for (int i = 0; i < totalSlices; i++) {
      final slice = _currentScan!.slices[i];
      
      _statusMessage = 'Scanning slice ${i + 1}/$totalSlices';
      _scanProgress = (i + 1) / totalSlices;
      notifyListeners();
      
      await _scanSlice(slice);
    }
  }
  
  /// Scan a single slice with the server
  Future<void> _scanSlice(CTSlice slice) async {
    try {
      // Send scan request to server
      final response = await http.post(
        Uri.parse('$_serverUrl/scan_slice'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'slice_index': slice.index,
        }),
      ).timeout(const Duration(seconds: 30));
      
      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }
      
      final result = jsonDecode(response.body);
      if (result['success'] != true) {
        throw Exception(result['error'] ?? 'Unknown error');
      }
      
      // Parse results
      final overlayBytes = base64Decode(result['overlay'] as String);
      
      slice.updateResults(
        hasPancreas: result['has_pancreas'] as bool,
        hasTumor: result['has_tumor'] as bool,
        pancreasPixels: result['pancreas_pixels'] as int,
        tumorPixels: result['tumor_pixels'] as int,
        overlayBytes: overlayBytes,
      );
      
    } catch (e) {
      debugPrint('Error scanning slice ${slice.index}: $e');
      rethrow;
    }
  }
  
  /// Reset tumor context on server (for non-sequential scanning)
  Future<void> resetContext() async {
    if (!_isServerReady) return;
    
    try {
      await http.post(
        Uri.parse('$_serverUrl/reset_context'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));
      
      debugPrint('Tumor context reset');
    } catch (e) {
      debugPrint('Error resetting context: $e');
    }
  }
  
  /// Clear current scan
  /// Generate 3D model from accumulated segmentation masks
  Future<String?> generate3DModel() async {
    if (_currentScan == null || !_currentScan!.isFullyScanned) {
      debugPrint('Cannot generate 3D model: scan not complete');
      return null;
    }
    
    try {
      _isLoading = true;
      _statusMessage = 'Generating 3D model...';
      notifyListeners();
      
      // Step 1: Request 3D model generation
      final response = await http.post(
        Uri.parse('$_serverUrl/generate_3d_model'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 120)); // Mesh generation takes time
      
      if (response.statusCode != 200) {
        throw Exception('Server error: ${response.statusCode}');
      }
      
      final data = jsonDecode(response.body);
      
      if (data['success'] != true) {
        throw Exception(data['error'] ?? 'Failed to generate 3D model');
      }
      
      debugPrint('3D model generated: ${data['size_bytes']} bytes');
      
      // Step 2: Fetch the actual GLB file
      final modelUrl = data['model_url'] as String;
      debugPrint('Fetching model from: $modelUrl');
      
      final modelResponse = await http.get(Uri.parse(modelUrl))
          .timeout(const Duration(seconds: 30));
      
      if (modelResponse.statusCode != 200) {
        throw Exception('Failed to fetch model: ${modelResponse.statusCode}');
      }
      
      // Convert to base64 data URL
      final base64Data = base64Encode(modelResponse.bodyBytes);
      final dataUrl = 'data:model/gltf-binary;base64,$base64Data';
      
      _statusMessage = 'Ready';
      _isLoading = false;
      notifyListeners();
      
      debugPrint('3D model ready as data URL: ${base64Data.length} chars');
      return dataUrl;
      
    } catch (e) {
      _statusMessage = 'Failed to generate 3D model';
      _isLoading = false;
      notifyListeners();
      debugPrint('Error generating 3D model: $e');
      return null;
    }
  }
  
  void clearScan() {
    _currentScan = null;
    _scanProgress = 0.0;
    _statusMessage = 'Ready';
    notifyListeners();
  }
}
