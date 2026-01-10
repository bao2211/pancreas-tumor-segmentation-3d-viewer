import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'dart:io';

/// Mobile-specific TFLite implementation
class MobileMLService {
  static const int inputSize = 128;
  static const int numClasses = 2;

  /// Load TFLite model
  static Future<Interpreter> loadModel() async {
    // Try loading from asset directly first
    try {
      return await Interpreter.fromAsset('models/unet_model.tflite');
    } catch (e) {
      // Fall back to copying to temp file
      final tempDir = await getTemporaryDirectory();
      final modelPath = path.join(tempDir.path, 'unet_model.tflite');
      final modelFile = File(modelPath);

      if (!await modelFile.exists()) {
        final byteData = await rootBundle.load('assets/models/unet_model.tflite');
        await modelFile.writeAsBytes(byteData.buffer.asUint8List());
      }

      return Interpreter.fromFile(modelFile);
    }
  }

  /// Run inference with TFLite interpreter
  static Future<SegmentationResult> runInference(
    Interpreter interpreter,
    img.Image image,
  ) async {
    final originalWidth = image.width;
    final originalHeight = image.height;

    // Resize to model input size
    final resized = img.copyResize(
      image,
      width: inputSize,
      height: inputSize,
      interpolation: img.Interpolation.linear,
    );

    // Preprocess - create input tensor [1, 128, 128, 1]
    final input = Float32List(1 * inputSize * inputSize * 1);
    int pixelIndex = 0;
    
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final pixel = resized.getPixel(x, y);
        
        // Convert to grayscale
        final gray = (0.299 * pixel.r + 0.587 * pixel.g + 0.114 * pixel.b);
        
        // Normalize to [0, 1]
        input[pixelIndex++] = gray / 255.0;
      }
    }

    // Reshape input
    final inputTensor = input.reshape([1, inputSize, inputSize, 1]);

    // Prepare output tensor [1, 128, 128, 2]
    final output = List.generate(
      1,
      (_) => List.generate(
        inputSize,
        (_) => List.generate(inputSize, (_) => List.filled(numClasses, 0.0)),
      ),
    );

    // Run inference
    interpreter.run(inputTensor, output);

    // Create binary mask
    final mask = Uint8List(inputSize * inputSize);
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        final bg = output[0][y][x][0];
        final tumor = output[0][y][x][1];
        mask[y * inputSize + x] = tumor > bg ? 1 : 0;
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

  /// Dispose interpreter
  static void dispose(Interpreter interpreter) {
    interpreter.close();
  }
}

/// Result class (duplicated for mobile module)
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
