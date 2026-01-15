import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:image/image.dart' as img;
import 'package:http/http.dart' as http;
import '../utils/platform_utils.dart';

/// Cross-platform ML Service for Pancreas Tumor Segmentation
/// Uses HTTP backend for Desktop, Android, and Web (connects to inference_server.py)
class MLService extends ChangeNotifier {
  bool _isModelLoaded = false;
  bool _isProcessing = false;
  String _statusMessage = 'Not initialized';
  String _serverUrl = 'http://localhost:8765'; // Default for desktop

  // Model input/output specifications
  static const int inputSize = 128;
  static const int numClasses = 2;

  bool get isModelLoaded => _isModelLoaded;
  bool get isProcessing => _isProcessing;
  String get statusMessage => _statusMessage;
  String get serverUrl => _serverUrl;
  bool get isDesktop => PlatformUtils.isDesktop;
  bool get isWeb => PlatformUtils.isWeb;

  /// Set server URL for Android (PC's IP address on same network)
  void setServerUrl(String url) {
    _serverUrl = url;
    notifyListeners();
  }

  /// Initialize the model / check server connection
  Future<void> loadModel() async {
    try {
      _statusMessage = 'Connecting to server...';
      notifyListeners();

      await _checkServer();
    } catch (e) {
      _statusMessage = 'Failed to connect: $e';
      _isModelLoaded = false;
      debugPrint('Error connecting to server: $e');
      notifyListeners();
    }
  }

  /// Check if inference server is running
  Future<void> _checkServer() async {
    try {
      final response = await http
          .get(Uri.parse('$_serverUrl/health'))
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        _isModelLoaded = true;
        _statusMessage = 'Connected to server';
        debugPrint('Server connected at $_serverUrl');
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (e) {
      _isModelLoaded = false;
      if (isWeb) {
        _statusMessage = 'Server not reachable. Check CORS settings.';
      } else if (isDesktop) {
        _statusMessage = 'Start inference_server.py first!';
      } else {
        _statusMessage = 'Server not reachable. Check IP address.';
      }
      debugPrint('Server not available: $e');
    }
    notifyListeners();
  }

  /// Run segmentation inference on image bytes (cross-platform)
  Future<SegmentationResult?> runInferenceOnBytes(Uint8List bytes) async {
    if (!_isModelLoaded) {
      _statusMessage = 'Server not connected';
      notifyListeners();
      return null;
    }

    try {
      _isProcessing = true;
      _statusMessage = 'Processing...';
      notifyListeners();

      // Decode image to get original dimensions
      final image = img.decodeImage(bytes);
      if (image == null) {
        throw Exception('Failed to decode image');
      }
      final originalWidth = image.width;
      final originalHeight = image.height;

      // Send to server for inference
      final base64Image = base64Encode(bytes);
      final result = await _runServerInference(base64Image, originalWidth, originalHeight);

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

  /// Run inference via HTTP server
  Future<SegmentationResult> _runServerInference(
      String base64Image, int originalWidth, int originalHeight) async {
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

    // Use raw mask data directly (array of 0s and 1s)
    // This avoids PNG decoding issues with the image package
    final maskRawB64 = result['mask_raw'] as String?;
    final serverTumorPixels = result['tumor_pixels'] as int?;
    
    Uint8List mask;
    
    if (maskRawB64 != null) {
      // Use raw mask bytes directly
      mask = base64Decode(maskRawB64);
      debugPrint('Using raw mask data: ${mask.length} bytes');
      debugPrint('Server reported tumor pixels: $serverTumorPixels');
      
      // Debug: check unique values in mask
      final uniqueValues = <int>{};
      int tumorCount = 0;
      for (int i = 0; i < mask.length && i < 100; i++) {
        uniqueValues.add(mask[i]);
      }
      for (int i = 0; i < mask.length; i++) {
        if (mask[i] == 1) tumorCount++;
      }
      debugPrint('Unique mask values in first 100 bytes: $uniqueValues');
      debugPrint('Flutter counted tumor pixels (==1): $tumorCount');
      debugPrint('First 20 mask values: ${mask.sublist(0, 20).join(", ")}');
    } else {
      // Fallback to PNG decoding (legacy)
      final maskBytes = base64Decode(result['mask']);
      final maskImage = img.decodePng(maskBytes);

      if (maskImage == null) {
        throw Exception('Failed to decode mask');
      }

      mask = Uint8List(inputSize * inputSize);
      for (int y = 0; y < inputSize; y++) {
        for (int x = 0; x < inputSize; x++) {
          final pixel = maskImage.getPixel(x, y);
          mask[y * inputSize + x] = pixel.rNormalized > 0.5 ? 1 : 0;
        }
      }
    }

    // Get server-generated overlay if available
    Uint8List? overlayBytes;
    final overlayB64 = result['overlay'] as String?;
    if (overlayB64 != null) {
      overlayBytes = base64Decode(overlayB64);
      debugPrint('Server provided overlay image: ${overlayBytes.length} bytes');
    }

    return SegmentationResult(
      mask: mask,
      maskWidth: inputSize,
      maskHeight: inputSize,
      originalWidth: originalWidth,
      originalHeight: originalHeight,
      overlayBytes: overlayBytes,
    );
  }

}

/// Result of segmentation inference
class SegmentationResult {
  final Uint8List mask;
  final int maskWidth;
  final int maskHeight;
  final int originalWidth;
  final int originalHeight;
  final Uint8List? overlayBytes; // Server-generated overlay image

  SegmentationResult({
    required this.mask,
    required this.maskWidth,
    required this.maskHeight,
    required this.originalWidth,
    required this.originalHeight,
    this.overlayBytes,
  });

  int get tumorPixelCount => mask.where((p) => p == 1).length;
  double get tumorPercentage =>
      (tumorPixelCount / (maskWidth * maskHeight)) * 100;
}
