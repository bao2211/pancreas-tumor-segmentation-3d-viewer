import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import 'package:http/http.dart' as http;

// Conditional import for TFLite - only available on mobile
import 'ml_service_mobile.dart' if (dart.library.html) 'ml_service_stub.dart';

/// Cross-platform ML Service
/// Uses TFLite on Android/iOS and HTTP backend on Windows/Desktop
class MLService extends ChangeNotifier {
  bool _isModelLoaded = false;
  bool _isProcessing = false;
  String _statusMessage = 'Not initialized';
  bool _isDesktop = false;
  
  // HTTP server settings for desktop
  static const String _serverHost = 'localhost';
  static const int _serverPort = 8765;
  static const String _serverUrl = 'http://$_serverHost:$_serverPort';
  
  // Model specifications
  static const int inputSize = 128;
  static const int numClasses = 2;
  
  // Mobile TFLite interpreter (null on desktop)
  dynamic _mobileInterpreter;

  bool get isModelLoaded => _isModelLoaded;
  bool get isProcessing => _isProcessing;
  String get statusMessage => _statusMessage;
  bool get isDesktop => _isDesktop;

  /// Initialize the service
  Future<void> initialize() async {
    _isDesktop = Platform.isWindows || Platform.isLinux || Platform.isMacOS;
    
    if (_isDesktop) {
      _statusMessage = 'Desktop mode - checking server...';
      notifyListeners();
      await _checkDesktopServer();
    } else {
      _statusMessage = 'Mobile mode - loading TFLite...';
      notifyListeners();
      await _loadMobileModel();
    }
  }

  /// Load model for mobile (TFLite)
  Future<void> _loadMobileModel() async {
    try {
      _statusMessage = 'Loading TFLite model...';
      notifyListeners();
      
      _mobileInterpreter = await MobileMLService.loadModel();
      
      _isModelLoaded = true;
      _statusMessage = 'Model loaded (TFLite)';
      notifyListeners();
    } catch (e) {
      _statusMessage = 'TFLite load failed: $e';
      _isModelLoaded = false;
      debugPrint('Mobile model error: $e');
      notifyListeners();
    }
  }

  /// Check desktop server availability
  Future<void> _checkDesktopServer() async {
    try {
      final response = await http.get(
        Uri.parse('$_serverUrl/health'),
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        _isModelLoaded = true;
        _statusMessage = 'Connected to inference server';
      } else {
        _isModelLoaded = false;
        _statusMessage = 'Server not responding. Start inference_server.py';
      }
    } catch (e) {
      _isModelLoaded = false;
      _statusMessage = 'Server not running.\nStart: python inference_server.py';
    }
    notifyListeners();
  }

  /// Reload/reconnect model
  Future<void> loadModel() async {
    await initialize();
  }

  /// Run segmentation inference on image file
  Future<SegmentationResult?> runInference(File imageFile) async {
    if (!_isModelLoaded) {
      _statusMessage = 'Model not loaded';
      notifyListeners();
      return null;
    }

    _isProcessing = true;
    _statusMessage = 'Processing...';
    notifyListeners();

    try {
      SegmentationResult result;
      
      if (_isDesktop) {
        result = await _runDesktopInference(imageFile);
      } else {
        result = await _runMobileInference(imageFile);
      }
      
      _isProcessing = false;
      _statusMessage = 'Segmentation complete!';
      notifyListeners();
      
      return result;
    } catch (e) {
      _isProcessing = false;
      _statusMessage = 'Error: $e';
      debugPrint('Inference error: $e');
      notifyListeners();
      return null;
    }
  }

  /// Desktop inference via HTTP server
  Future<SegmentationResult> _runDesktopInference(File imageFile) async {
    // Read and encode image
    final bytes = await imageFile.readAsBytes();
    final image = img.decodeImage(bytes);
    
    if (image == null) {
      throw Exception('Failed to decode image');
    }
    
    final originalWidth = image.width;
    final originalHeight = image.height;
    
    // Convert to PNG and base64 encode
    final pngBytes = img.encodePng(image);
    final base64Image = base64Encode(pngBytes);
    
    // Send to server
    final response = await http.post(
      Uri.parse('$_serverUrl/segment'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'image': base64Image}),
    ).timeout(const Duration(seconds: 60));
    
    if (response.statusCode != 200) {
      throw Exception('Server error: ${response.statusCode}');
    }
    
    final result = jsonDecode(response.body);
    
    if (result['success'] != true) {
      throw Exception(result['error'] ?? 'Unknown error');
    }
    
    // Decode mask
    final maskBytes = base64Decode(result['mask']);
    final maskImage = img.decodePng(maskBytes);
    
    if (maskImage == null) {
      throw Exception('Failed to decode mask');
    }
    
    // Convert to binary mask
    final mask = Uint8List(inputSize * inputSize);
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = maskImage.getPixel(x, y);
        mask[y * inputSize + x] = pixel.r > 127 ? 1 : 0;
      }
    }
    
    return SegmentationResult(
      mask: mask,
      maskWidth: inputSize,
      maskHeight: inputSize,
      originalWidth: originalWidth,
      originalHeight: originalHeight,
    );
  }

  /// Mobile inference via TFLite
  Future<SegmentationResult> _runMobileInference(File imageFile) async {
    final bytes = await imageFile.readAsBytes();
    final image = img.decodeImage(bytes);
    
    if (image == null) {
      throw Exception('Failed to decode image');
    }
    
    return MobileMLService.runInference(
      _mobileInterpreter,
      image,
    );
  }

  @override
  void dispose() {
    if (!_isDesktop && _mobileInterpreter != null) {
      MobileMLService.dispose(_mobileInterpreter);
    }
    super.dispose();
  }
}

/// Result of segmentation inference
class SegmentationResult {
  final Uint8List mask;
  final int maskWidth;
  final int maskHeight;
  final int originalWidth;
  final int originalHeight;

  SegmentationResult({
    required this.mask,
    required this.maskWidth,
    required this.maskHeight,
    required this.originalWidth,
    required this.originalHeight,
  });

  int get tumorPixelCount => mask.where((p) => p == 1).length;
  double get tumorPercentage =>
      (tumorPixelCount / (maskWidth * maskHeight)) * 100;
}
