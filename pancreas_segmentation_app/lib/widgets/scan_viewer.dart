import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import '../services/ml_service.dart';
import '../theme/app_theme.dart';

class ScanViewer extends StatefulWidget {
  final File imageFile;
  final SegmentationResult? segmentationResult;
  final bool showOverlay;

  const ScanViewer({
    super.key,
    required this.imageFile,
    this.segmentationResult,
    this.showOverlay = true,
  });

  @override
  State<ScanViewer> createState() => _ScanViewerState();
}

class _ScanViewerState extends State<ScanViewer> {
  final TransformationController _transformController = TransformationController();
  double _currentScale = 1.0;

  @override
  void dispose() {
    _transformController.dispose();
    super.dispose();
  }

  void _resetZoom() {
    _transformController.value = Matrix4.identity();
    setState(() => _currentScale = 1.0);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 500,
      color: const Color(0xFF0A0E14),
      child: Stack(
        children: [
          // Grid Background
          CustomPaint(
            size: const Size(double.infinity, 500),
            painter: _GridPainter(),
          ),
          
          // Interactive Image Viewer
          InteractiveViewer(
            transformationController: _transformController,
            minScale: 0.5,
            maxScale: 4.0,
            onInteractionUpdate: (details) {
              setState(() {
                _currentScale = _transformController.value.getMaxScaleOnAxis();
              });
            },
            child: Center(
              child: _buildImageStack(),
            ),
          ),
          
          // Top Info Bar
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withOpacity(0.7),
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
                      widget.imageFile.path.split(Platform.pathSeparator).last,
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
          
          // Bottom Controls Bar
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    Colors.black.withOpacity(0.7),
                    Colors.transparent,
                  ],
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildControlButton(Icons.remove, () {
                    final newScale = (_currentScale - 0.25).clamp(0.5, 4.0);
                    _transformController.value = Matrix4.identity()..scale(newScale);
                    setState(() => _currentScale = newScale);
                  }),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceCard,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${(_currentScale * 100).toInt()}%',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppTheme.textPrimary,
                        fontFamily: 'Consolas',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  _buildControlButton(Icons.add, () {
                    final newScale = (_currentScale + 0.25).clamp(0.5, 4.0);
                    _transformController.value = Matrix4.identity()..scale(newScale);
                    setState(() => _currentScale = newScale);
                  }),
                  const SizedBox(width: 16),
                  _buildControlButton(Icons.fit_screen, _resetZoom),
                ],
              ),
            ),
          ),
          
          // Legend (when overlay is shown)
          if (widget.segmentationResult != null && widget.showOverlay)
            Positioned(
              bottom: 60,
              right: 16,
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceCard.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.surfaceCardHover),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildLegendItem('Detected Tumor', AppTheme.tumorRed),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildImageStack() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Stack(
          alignment: Alignment.center,
          children: [
            // Original Image
            Image.file(
              widget.imageFile,
              fit: BoxFit.contain,
              filterQuality: FilterQuality.high,
            ),
            
            // Overlay Mask - must match the exact size and position of the original image
            if (widget.segmentationResult != null && widget.showOverlay)
              Positioned.fill(
                child: Opacity(
                  opacity: 0.5,
                  child: Image.memory(
                    _createMaskImage(),
                    fit: BoxFit.contain,
                    filterQuality: FilterQuality.high,
                  ),
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _buildBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.5)),
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

  Widget _buildControlButton(IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(6),
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppTheme.surfaceCard,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Icon(icon, size: 18, color: AppTheme.textSecondary),
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: AppTheme.textSecondary,
          ),
        ),
      ],
    );
  }

  /// Create mask image from segmentation result
  /// The mask is resized to match the original image dimensions for proper overlay
  Uint8List _createMaskImage() {
    final result = widget.segmentationResult!;
    
    // Create mask at original image size for proper alignment
    final targetWidth = result.originalWidth;
    final targetHeight = result.originalHeight;
    
    final maskImage = img.Image(
      width: targetWidth, 
      height: targetHeight,
      numChannels: 4,
    );
    
    // Scale factors from mask (128x128) to original size
    final scaleX = result.maskWidth / targetWidth;
    final scaleY = result.maskHeight / targetHeight;
    
    // First pass: Create a scaled mask array to detect edges
    final scaledMask = List.generate(targetHeight, (_) => List.filled(targetWidth, false));
    
    for (int y = 0; y < targetHeight; y++) {
      for (int x = 0; x < targetWidth; x++) {
        final maskX = (x * scaleX).floor().clamp(0, result.maskWidth - 1);
        final maskY = (y * scaleY).floor().clamp(0, result.maskHeight - 1);
        final idx = maskY * result.maskWidth + maskX;
        scaledMask[y][x] = result.mask[idx] == 1;
      }
    }
    
    // Second pass: Fill with color and detect edges for outline
    for (int y = 0; y < targetHeight; y++) {
      for (int x = 0; x < targetWidth; x++) {
        if (scaledMask[y][x]) {
          // Check if this is an edge pixel (has a non-tumor neighbor)
          bool isEdge = false;
          for (int dy = -1; dy <= 1 && !isEdge; dy++) {
            for (int dx = -1; dx <= 1 && !isEdge; dx++) {
              if (dx == 0 && dy == 0) continue;
              final nx = x + dx;
              final ny = y + dy;
              if (nx < 0 || nx >= targetWidth || ny < 0 || ny >= targetHeight) {
                isEdge = true;
              } else if (!scaledMask[ny][nx]) {
                isEdge = true;
              }
            }
          }
          
          if (isEdge) {
            // Bright yellow outline
            maskImage.setPixelRgba(x, y, 255, 255, 0, 255);
          } else {
            // Bright red fill with good visibility
            maskImage.setPixelRgba(x, y, 255, 50, 50, 160);
          }
        } else {
          // Background - transparent
          maskImage.setPixelRgba(x, y, 0, 0, 0, 0);
        }
      }
    }
    
    return Uint8List.fromList(img.encodePng(maskImage));
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.03)
      ..strokeWidth = 1;

    const spacing = 20.0;
    
    for (double x = 0; x < size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
