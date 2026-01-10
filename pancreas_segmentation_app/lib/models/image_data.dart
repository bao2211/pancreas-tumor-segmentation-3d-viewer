import 'dart:typed_data';

/// Cross-platform image data that works on web, desktop, and mobile
class ImageData {
  final Uint8List bytes;
  final String name;
  final String? path;

  ImageData({
    required this.bytes,
    required this.name,
    this.path,
  });

  /// Get display name (filename without path)
  String get displayName => name;
}
