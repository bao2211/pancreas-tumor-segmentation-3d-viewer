import 'dart:typed_data';

/// Represents a loaded NIfTI CT scan
class NiiScan {
  final String fileName;
  final List<CTSlice> slices;
  final List<int> volumeShape;
  
  NiiScan({
    required this.fileName,
    required this.slices,
    required this.volumeShape,
  });
  
  int get numSlices => slices.length;
  
  int get numScanned => slices.where((s) => s.isScanned).length;
  
  int get numWithPancreas => slices.where((s) => s.hasPancreas).length;
  
  int get numWithTumor => slices.where((s) => s.hasTumor).length;
  
  bool get hasAnyTumor => slices.any((s) => s.hasTumor);
  
  bool get isFullyScanned => slices.every((s) => s.isScanned);
  
  /// Total pancreas pixels across all slices
  int get totalPancreasPixels => slices
      .where((s) => s.isScanned)
      .fold(0, (sum, s) => sum + s.pancreasPixels);
  
  /// Total tumor pixels across all slices
  int get totalTumorPixels => slices
      .where((s) => s.isScanned)
      .fold(0, (sum, s) => sum + s.tumorPixels);
  
  /// Tumor burden: percentage of tumor pixels relative to pancreas pixels
  double get tumorBurden {
    if (totalPancreasPixels == 0) return 0.0;
    return (totalTumorPixels / totalPancreasPixels) * 100;
  }
  
  /// Percentage of slices with pancreas
  double get pancreasSlicePercentage {
    if (numScanned == 0) return 0.0;
    return (numWithPancreas / numScanned) * 100;
  }
  
  /// Percentage of slices with tumor
  double get tumorSlicePercentage {
    if (numScanned == 0) return 0.0;
    return (numWithTumor / numScanned) * 100;
  }
  
  /// Estimated volume dimensions (assuming standard CT spacing)
  String get volumeDimensions => '${volumeShape[0]} × ${volumeShape[1]} × ${volumeShape[2]}';
  
  /// Average tumor pixels per affected slice
  double get avgTumorPixelsPerSlice {
    if (numWithTumor == 0) return 0.0;
    return totalTumorPixels / numWithTumor;
  }
  
  /// Maximum tumor pixels in a single slice
  int get maxTumorPixelsInSlice => slices
      .where((s) => s.isScanned && s.hasTumor)
      .fold(0, (max, s) => s.tumorPixels > max ? s.tumorPixels : max);
  
  /// Index of slice with maximum tumor
  int? get maxTumorSliceIndex {
    if (numWithTumor == 0) return null;
    final maxSlice = slices
        .where((s) => s.isScanned && s.hasTumor)
        .reduce((a, b) => a.tumorPixels > b.tumorPixels ? a : b);
    return maxSlice.index;
  }
}

/// Represents a single CT slice from the scan
class CTSlice {
  final int index;
  final Uint8List imageBytes; // Preview image (grayscale PNG)
  final List<int> shape;
  
  // Scan results
  bool isScanned;
  bool hasPancreas;
  bool hasTumor;
  int pancreasPixels;
  int tumorPixels;
  Uint8List? overlayBytes; // Overlay with contours
  
  CTSlice({
    required this.index,
    required this.imageBytes,
    required this.shape,
    this.isScanned = false,
    this.hasPancreas = false,
    this.hasTumor = false,
    this.pancreasPixels = 0,
    this.tumorPixels = 0,
    this.overlayBytes,
  });
  
  /// Update with scan results
  void updateResults({
    required bool hasPancreas,
    required bool hasTumor,
    required int pancreasPixels,
    required int tumorPixels,
    Uint8List? overlayBytes,
  }) {
    isScanned = true;
    this.hasPancreas = hasPancreas;
    this.hasTumor = hasTumor;
    this.pancreasPixels = pancreasPixels;
    this.tumorPixels = tumorPixels;
    this.overlayBytes = overlayBytes;
  }
  
  String get status {
    if (!isScanned) return 'Not scanned';
    if (hasTumor) return '⚠️ Tumor detected';
    if (hasPancreas) return '✓ Pancreas only';
    return 'No pancreas';
  }
}
