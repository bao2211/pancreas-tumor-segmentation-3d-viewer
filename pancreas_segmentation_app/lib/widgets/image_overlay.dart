import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/ml_service.dart';

/// Widget to display image with segmentation overlay
class ImageOverlay extends StatelessWidget {
  final File imageFile;
  final SegmentationResult? segmentationResult;
  final Color overlayColor;
  final double overlayOpacity;

  const ImageOverlay({
    super.key,
    required this.imageFile,
    this.segmentationResult,
    this.overlayColor = Colors.red,
    this.overlayOpacity = 0.5,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Original image
        Image.file(
          imageFile,
          fit: BoxFit.contain,
          filterQuality: FilterQuality.high,
        ),

        // Segmentation overlay
        if (segmentationResult != null)
          CustomPaint(
            painter: SegmentationOverlayPainter(
              mask: segmentationResult!.mask,
              maskWidth: segmentationResult!.maskWidth,
              maskHeight: segmentationResult!.maskHeight,
              overlayColor: overlayColor,
              overlayOpacity: overlayOpacity,
            ),
          ),
      ],
    );
  }
}

/// Custom painter for segmentation mask overlay
class SegmentationOverlayPainter extends CustomPainter {
  final Uint8List mask;
  final int maskWidth;
  final int maskHeight;
  final Color overlayColor;
  final double overlayOpacity;

  SegmentationOverlayPainter({
    required this.mask,
    required this.maskWidth,
    required this.maskHeight,
    required this.overlayColor,
    required this.overlayOpacity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = overlayColor.withOpacity(overlayOpacity)
      ..style = PaintingStyle.fill;

    // Calculate scale factors
    final scaleX = size.width / maskWidth;
    final scaleY = size.height / maskHeight;

    // Draw each tumor pixel as a rectangle
    for (int y = 0; y < maskHeight; y++) {
      for (int x = 0; x < maskWidth; x++) {
        final index = y * maskWidth + x;
        if (mask[index] == 1) {
          // This pixel is tumor
          final rect = Rect.fromLTWH(
            x * scaleX,
            y * scaleY,
            scaleX + 0.5, // Slight overlap to avoid gaps
            scaleY + 0.5,
          );
          canvas.drawRect(rect, paint);
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant SegmentationOverlayPainter oldDelegate) {
    return mask != oldDelegate.mask ||
        overlayColor != oldDelegate.overlayColor ||
        overlayOpacity != oldDelegate.overlayOpacity;
  }
}

/// Widget to display side-by-side comparison
class ComparisonView extends StatelessWidget {
  final File imageFile;
  final SegmentationResult? segmentationResult;

  const ComparisonView({
    super.key,
    required this.imageFile,
    this.segmentationResult,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Original image
        Expanded(
          child: Column(
            children: [
              Text(
                'Original',
                style: Theme.of(context).textTheme.labelMedium,
              ),
              const SizedBox(height: 4),
              Expanded(
                child: Image.file(
                  imageFile,
                  fit: BoxFit.contain,
                ),
              ),
            ],
          ),
        ),

        const SizedBox(width: 8),

        // With overlay
        Expanded(
          child: Column(
            children: [
              Text(
                'Segmentation',
                style: Theme.of(context).textTheme.labelMedium,
              ),
              const SizedBox(height: 4),
              Expanded(
                child: ImageOverlay(
                  imageFile: imageFile,
                  segmentationResult: segmentationResult,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Mask visualization widget (shows just the mask)
class MaskView extends StatelessWidget {
  final SegmentationResult result;
  final Color tumorColor;
  final Color backgroundColor;

  const MaskView({
    super.key,
    required this.result,
    this.tumorColor = Colors.red,
    this.backgroundColor = Colors.black,
  });

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: MaskPainter(
        mask: result.mask,
        maskWidth: result.maskWidth,
        maskHeight: result.maskHeight,
        tumorColor: tumorColor,
        backgroundColor: backgroundColor,
      ),
    );
  }
}

class MaskPainter extends CustomPainter {
  final Uint8List mask;
  final int maskWidth;
  final int maskHeight;
  final Color tumorColor;
  final Color backgroundColor;

  MaskPainter({
    required this.mask,
    required this.maskWidth,
    required this.maskHeight,
    required this.tumorColor,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final bgPaint = Paint()..color = backgroundColor;
    final tumorPaint = Paint()..color = tumorColor;

    // Fill background
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), bgPaint);

    // Calculate scale
    final scaleX = size.width / maskWidth;
    final scaleY = size.height / maskHeight;

    // Draw tumor pixels
    for (int y = 0; y < maskHeight; y++) {
      for (int x = 0; x < maskWidth; x++) {
        if (mask[y * maskWidth + x] == 1) {
          canvas.drawRect(
            Rect.fromLTWH(x * scaleX, y * scaleY, scaleX + 0.5, scaleY + 0.5),
            tumorPaint,
          );
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant MaskPainter oldDelegate) {
    return mask != oldDelegate.mask;
  }
}
