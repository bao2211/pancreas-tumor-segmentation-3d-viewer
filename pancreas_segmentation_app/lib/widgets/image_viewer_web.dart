import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import '../services/ml_service.dart';
import '../theme/app_theme.dart';

/// Cross-platform image viewer that works with bytes instead of File
class ImageViewerWeb extends StatefulWidget {
  final Uint8List imageBytes;
  final String imageName;
  final SegmentationResult? segmentationResult;
  final bool showOverlay;

  const ImageViewerWeb({
    super.key,
    required this.imageBytes,
    required this.imageName,
    this.segmentationResult,
    this.showOverlay = true,
  });

  @override
  State<ImageViewerWeb> createState() => _ImageViewerWebState();
}

class _ImageViewerWebState extends State<ImageViewerWeb> {
  Uint8List? _overlayBytes;
  bool _isGeneratingOverlay = false;

  @override
  void didUpdateWidget(ImageViewerWeb oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.segmentationResult != oldWidget.segmentationResult) {
      _generateOverlay();
    }
  }

  @override
  void initState() {
    super.initState();
    if (widget.segmentationResult != null) {
      _generateOverlay();
    }
  }

  Future<void> _generateOverlay() async {
    if (widget.segmentationResult == null) {
      setState(() => _overlayBytes = null);
      return;
    }

    setState(() => _isGeneratingOverlay = true);

    try {
      final result = widget.segmentationResult!;
      
      // Use server-generated overlay if available (preferred for web)
      if (result.overlayBytes != null) {
        debugPrint('Using server-generated overlay');
        setState(() {
          _overlayBytes = result.overlayBytes;
          _isGeneratingOverlay = false;
        });
        return;
      }
      
      // Fallback: Generate overlay client-side
      debugPrint('Generating overlay client-side (fallback)');
      final originalImage = img.decodeImage(widget.imageBytes);
      
      if (originalImage == null) {
        setState(() {
          _overlayBytes = null;
          _isGeneratingOverlay = false;
        });
        return;
      }

      // Create overlay image
      final overlayImage = img.Image(
        width: originalImage.width,
        height: originalImage.height,
      );

      // Calculate scale factors
      final scaleX = originalImage.width / result.maskWidth;
      final scaleY = originalImage.height / result.maskHeight;
      
      // Debug: count tumor pixels in mask
      int tumorPixels = 0;
      int backgroundPixels = 0;
      int sampleValue1 = result.mask[0];
      int sampleValue2 = result.mask[result.mask.length ~/ 2];
      int sampleValue3 = result.mask[result.mask.length - 1];
      
      for (int i = 0; i < result.mask.length; i++) {
        if (result.mask[i] > 0) {  // Changed from == 1 to > 0
          tumorPixels++;
        } else {
          backgroundPixels++;
        }
      }
      
      debugPrint('ImageViewerWeb: mask stats:');
      debugPrint('  Total pixels: ${result.mask.length}');
      debugPrint('  Tumor pixels (>0): $tumorPixels');
      debugPrint('  Background pixels (==0): $backgroundPixels');
      debugPrint('  Sample values: [0]=$sampleValue1, [mid]=$sampleValue2, [last]=$sampleValue3');

      // Copy original image and add red overlay for tumor regions
      int overlayTumorCount = 0;
      for (int y = 0; y < originalImage.height; y++) {
        for (int x = 0; x < originalImage.width; x++) {
          final originalPixel = originalImage.getPixel(x, y);
          
          // Get mask value at scaled position
          final maskX = (x / scaleX).floor().clamp(0, result.maskWidth - 1);
          final maskY = (y / scaleY).floor().clamp(0, result.maskHeight - 1);
          final maskIndex = maskY * result.maskWidth + maskX;
          final maskValue = result.mask[maskIndex];
          
          // Use luminance for grayscale value to ensure we handle single-channel images correctly
          // If the image is single channel, g and b might be 0, causing the "background" to look red
          final grayVal = originalPixel.luminanceNormalized;
          
          if (maskValue > 0) {
            overlayTumorCount++;
            // Tumor region - blend with red (50% gray + 50% red)
            // R: 0.5 * gray + 0.5 * 1.0 (red)
            final r = ((grayVal * 0.5 + 0.5) * 255).round().clamp(0, 255);
            // G, B: 0.5 * gray
            final g = (grayVal * 0.5 * 255).round().clamp(0, 255);
            final b = (grayVal * 0.5 * 255).round().clamp(0, 255);
            overlayImage.setPixelRgba(x, y, r, g, b, 255);
          } else {
            // Non-tumor region - keep original (grayscale)
            // Write the gray value to all R, G, B channels
            final val = (grayVal * 255).round().clamp(0, 255);
            overlayImage.setPixelRgba(x, y, val, val, val, 255);
          }
        }
      }

      debugPrint('ImageViewerWeb: overlay applied red to $overlayTumorCount pixels');
      
      final pngBytes = Uint8List.fromList(img.encodePng(overlayImage));
      
      setState(() {
        _overlayBytes = pngBytes;
        _isGeneratingOverlay = false;
      });
    } catch (e) {
      debugPrint('Error generating overlay: $e');
      setState(() {
        _overlayBytes = null;
        _isGeneratingOverlay = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Image
        Container(
          color: AppTheme.surfaceDark,
          child: _buildImage(),
        ),

        // Header overlay
        Positioned(
          top: 0,
          left: 0,
          right: 0,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.black.withValues(alpha: 0.7),
                  Colors.transparent,
                ],
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceCard,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    widget.imageName,
                    style: const TextStyle(
                      fontSize: 11,
                      color: AppTheme.textSecondary,
                      fontFamily: 'Consolas',
                    ),
                  ),
                ),
                const Spacer(),
                if (widget.segmentationResult != null)
                  _buildBadge(
                    widget.showOverlay ? 'AI Overlay' : 'Original',
                    widget.showOverlay ? AppTheme.accentTeal : AppTheme.textSecondary,
                  ),
              ],
            ),
          ),
        ),

        // Loading indicator
        if (_isGeneratingOverlay)
          const Center(
            child: CircularProgressIndicator(),
          ),
      ],
    );
  }

  Widget _buildImage() {
    final Uint8List displayBytes;
    
    if (widget.showOverlay && _overlayBytes != null) {
      displayBytes = _overlayBytes!;
    } else {
      displayBytes = widget.imageBytes;
    }

    return InteractiveViewer(
      minScale: 0.5,
      maxScale: 4.0,
      child: Center(
        child: Image.memory(
          displayBytes,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 48, color: AppTheme.error),
                  SizedBox(height: 16),
                  Text(
                    'Failed to load image',
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
