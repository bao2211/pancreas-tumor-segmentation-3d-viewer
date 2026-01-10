import 'dart:typed_data';
import 'package:image/image.dart' as img;

/// Stub for web platform (not supported)
class MobileMLService {
  static const int inputSize = 128;

  static Future<dynamic> loadModel() async {
    throw UnsupportedError('TFLite not supported on web');
  }

  static Future<SegmentationResult> runInference(
    dynamic interpreter,
    img.Image image,
  ) async {
    throw UnsupportedError('TFLite not supported on web');
  }

  static void dispose(dynamic interpreter) {}
}

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
