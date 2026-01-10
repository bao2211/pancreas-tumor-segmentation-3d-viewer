import 'dart:typed_data';
import 'dart:math' as math;

/// Image processing utilities for CT scan preprocessing
class ImageProcessing {
  /// Apply HU windowing to raw CT data
  /// Clips values to [-128, 127] and normalizes to [0, 1]
  static Float32List huWindow(Float32List data) {
    final result = Float32List(data.length);

    for (int i = 0; i < data.length; i++) {
      // Clip to HU window [-128, 127]
      double value = data[i].clamp(-128, 127);

      // Normalize to [0, 1]
      result[i] = (value + 128) / 255.0;
    }

    return result;
  }

  /// Resize 2D float data using bilinear interpolation
  static Float32List resize(
    Float32List data,
    int srcWidth,
    int srcHeight,
    int dstWidth,
    int dstHeight,
  ) {
    final result = Float32List(dstWidth * dstHeight);

    final xRatio = (srcWidth - 1) / (dstWidth - 1);
    final yRatio = (srcHeight - 1) / (dstHeight - 1);

    for (int y = 0; y < dstHeight; y++) {
      for (int x = 0; x < dstWidth; x++) {
        final srcX = x * xRatio;
        final srcY = y * yRatio;

        final x0 = srcX.floor();
        final y0 = srcY.floor();
        final x1 = math.min(x0 + 1, srcWidth - 1);
        final y1 = math.min(y0 + 1, srcHeight - 1);

        final xFrac = srcX - x0;
        final yFrac = srcY - y0;

        // Bilinear interpolation
        final v00 = data[y0 * srcWidth + x0];
        final v10 = data[y0 * srcWidth + x1];
        final v01 = data[y1 * srcWidth + x0];
        final v11 = data[y1 * srcWidth + x1];

        final v0 = v00 * (1 - xFrac) + v10 * xFrac;
        final v1 = v01 * (1 - xFrac) + v11 * xFrac;

        result[y * dstWidth + x] = v0 * (1 - yFrac) + v1 * yFrac;
      }
    }

    return result;
  }

  /// Normalize data to [0, 1] range
  static Float32List normalize(Float32List data) {
    if (data.isEmpty) return data;

    double minVal = data[0];
    double maxVal = data[0];

    for (final v in data) {
      if (v < minVal) minVal = v;
      if (v > maxVal) maxVal = v;
    }

    final range = maxVal - minVal;
    if (range == 0) {
      return Float32List(data.length); // All zeros
    }

    final result = Float32List(data.length);
    for (int i = 0; i < data.length; i++) {
      result[i] = (data[i] - minVal) / range;
    }

    return result;
  }

  /// Check if data appears to be already preprocessed (values in [0, 1])
  static bool isPreprocessed(Float32List data) {
    if (data.isEmpty) return false;

    double minVal = data[0];
    double maxVal = data[0];

    for (final v in data) {
      if (v < minVal) minVal = v;
      if (v > maxVal) maxVal = v;
    }

    // If all values are between 0 and 1, likely preprocessed
    return minVal >= -0.01 && maxVal <= 1.01;
  }

  /// Convert grayscale float data to RGBA bytes for display
  static Uint8List toRgba(Float32List data, int width, int height) {
    final result = Uint8List(width * height * 4);

    for (int i = 0; i < data.length; i++) {
      final gray = (data[i].clamp(0, 1) * 255).round();
      final offset = i * 4;
      result[offset] = gray; // R
      result[offset + 1] = gray; // G
      result[offset + 2] = gray; // B
      result[offset + 3] = 255; // A
    }

    return result;
  }

  /// Apply colormap to mask for visualization
  static Uint8List applyColormap(
    Uint8List mask,
    int width,
    int height, {
    int r = 255,
    int g = 0,
    int b = 0,
    int alpha = 128,
  }) {
    final result = Uint8List(width * height * 4);

    for (int i = 0; i < mask.length; i++) {
      final offset = i * 4;
      if (mask[i] > 0) {
        result[offset] = r;
        result[offset + 1] = g;
        result[offset + 2] = b;
        result[offset + 3] = alpha;
      } else {
        result[offset] = 0;
        result[offset + 1] = 0;
        result[offset + 2] = 0;
        result[offset + 3] = 0;
      }
    }

    return result;
  }
}
