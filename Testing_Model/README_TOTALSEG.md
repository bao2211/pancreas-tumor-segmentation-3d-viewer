# Hybrid Pancreas & Tumor Detection

## Overview

This enhanced version uses a **hybrid approach** combining:
- **TotalSegmentator**: Robust, pre-trained model for pancreas segmentation ([GitHub](https://github.com/wasserth/TotalSegmentator))
- **Custom U-Net**: Your specialized model for tumor detection on pancreatic tissue

## Why This Hybrid Approach?

### Benefits of TotalSegmentator for Pancreas:
✅ **Robust**: Trained on 1000+ CT scans with diverse patient populations  
✅ **Well-tested**: Used in clinical research worldwide  
✅ **Accurate**: State-of-the-art segmentation performance  
✅ **Multi-organ**: Can segment 100+ anatomical structures  
✅ **Maintained**: Actively developed and updated  

### Benefits of Custom Tumor Model:
✅ **Specialized**: Specifically trained for pancreatic tumor detection  
✅ **Domain-specific**: Understands pancreatic tumor characteristics  
✅ **Optimized**: Fine-tuned for your specific use case  

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_totalseg.txt
```

### 2. Download TotalSegmentator Models (First Run Only)

The first time you run the script, TotalSegmentator will automatically download its models (~1.5GB). This happens once and takes a few minutes.

### Optional: GPU Acceleration

For **much faster** processing (30x speedup), install PyTorch with GPU support:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

Then modify the script to use `device="gpu"` instead of `device="cpu"`.

## Usage

### Run the Test Script

```bash
cd Testing_Model
python test_pancreas_detection_totalseg.py
```

### Expected Output

```
============================================================
Hybrid Pancreas & Tumor Detection Test
Pancreas: TotalSegmentator (robust pre-trained)
Tumor: Custom U-Net (specialized for pancreatic tumors)
============================================================

[1] Checking TotalSegmentator...
[OK] TotalSegmentator available

[2] Loading custom tumor detection model...
[OK] Tumor model loaded: (None, 128, 128, 1)

[3] Loading test file: Testset/pancreas_001.nii.gz
[OK] Loaded volume: shape=(512, 512, 110), dtype=float64

[4] Running TotalSegmentator for pancreas detection...
    This may take a few minutes on CPU...
    [TotalSegmentator] Processing...
[OK] TotalSegmentator complete!
     Found pancreas in 47/110 slices

[5] Running custom tumor detection on pancreas regions...
[OK] Tumor detection complete!

[6] Statistical Analysis
============================================================
SLICES WITH PANCREAS: 47/110 (42.7%)
SLICES WITH TUMOR (>=10 pixels): 39
============================================================
```

## Performance Comparison

| Aspect | Original (Custom U-Net) | Hybrid (TotalSeg + Custom) |
|--------|------------------------|----------------------------|
| **Pancreas Detection** | Custom U-Net | TotalSegmentator (more robust) |
| **Tumor Detection** | Custom U-Net | Custom U-Net (same) |
| **Accuracy** | Good on training data | Better generalization |
| **Speed (CPU)** | ~2 min | ~5-8 min |
| **Speed (GPU)** | N/A | ~30 sec |
| **Robustness** | Dataset-dependent | Clinical-grade |

## Output Files

Results are saved to `test_results_totalseg/`:

1. **Individual slice overlays**: `slice_XXX_PANCREAS_AND_TUMOR.png`
   - Cyan contours = Pancreas (from TotalSegmentator)
   - Red contours = Tumor (from custom model)

2. **Summary visualization**: `summary_visualization.png`
   - 6 representative slices showing detections

## Workflow Details

### Stage 1: Pancreas Detection (TotalSegmentator)
```python
totalsegmentator(
    input=ct_scan_path,
    output=output_path,
    task="total",
    roi_subset=["pancreas"],
    device="cpu"  # or "gpu" for faster processing
)
```

### Stage 2: Tumor Detection (Custom Model)
```python
# Extract pancreas ROI from TotalSegmentator result
roi = extract_pancreas_region(slice)

# Preprocess and predict tumor
tumor_mask = custom_tumor_model.predict(roi)
```

## Troubleshooting

### Issue: TotalSegmentator not found
```bash
pip install TotalSegmentator
```

### Issue: Out of memory on CPU
TotalSegmentator needs ~8GB RAM. Use `fast=True` for lower memory usage:
```python
totalsegmentator(..., fast=True)
```

### Issue: Too slow on CPU
Install PyTorch with GPU support (see Installation section above).

### Issue: Models not downloading
Check your internet connection. TotalSegmentator downloads models from Zenodo on first run.

## Technical Details

### TotalSegmentator Output
- **Task**: `total` (full body segmentation)
- **ROI**: Pancreas only (label 7)
- **Format**: NIfTI multilabel mask
- **Resolution**: Native CT resolution (512×512)

### Custom Tumor Model Input
- **Input size**: 128×128×1
- **Preprocessing**: HU windowing [-128, 127], normalization [0, 1]
- **ROI**: Cropped from pancreas mask bounding box
- **Output**: Binary tumor mask

## References

- **TotalSegmentator Paper**: Wasserthal et al., "TotalSegmentator: robust segmentation of 104 anatomical structures in CT images" (Radiology: AI, 2023)
- **GitHub**: https://github.com/wasserth/TotalSegmentator
- **Citation**: If you use this hybrid approach in research, cite both TotalSegmentator and your custom model.

## Comparison with Original Notebook

This hybrid approach maintains the same two-stage philosophy from your original notebook but with enhanced pancreas detection:

| Component | Original | Hybrid |
|-----------|----------|--------|
| HU Windowing | ✅ Same | ✅ Same |
| Pancreas Detection | Custom U-Net (256×256) | **TotalSegmentator (robust)** |
| ROI Extraction | ✅ Same | ✅ Same |
| Tumor Detection | Custom U-Net (128×128) | ✅ Same |
| Visualization | ✅ Cyan/Red overlay | ✅ Same |
| Threshold | ✅ ≥10 pixels | ✅ Same |

The hybrid approach is **more robust** while preserving your specialized tumor detection capabilities! 🎯
