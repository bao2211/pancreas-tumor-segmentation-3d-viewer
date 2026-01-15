# Pancreas & Tumor Detection Testing Suite

## 📁 Contents

This folder contains two approaches for pancreas and tumor detection:

### 🔵 Method 1: Original (Custom U-Net)
**Files:**
- `test_pancreas_detection.py` - Original test script using custom U-Net for both pancreas and tumor

**Approach:**
- Stage 1: Custom U-Net (256×256) for pancreas detection
- Stage 2: Custom U-Net (128×128) for tumor detection

**Results:** Saved to `test_results/`

### 🟢 Method 2: Hybrid (TotalSegmentator + Custom)
**Files:**
- `test_pancreas_detection_totalseg.py` - **NEW** Hybrid approach using TotalSegmentator
- `requirements_totalseg.txt` - Dependencies for TotalSegmentator
- `README_TOTALSEG.md` - Detailed documentation for hybrid method
- `install_totalseg.bat` - Windows installation script

**Approach:**
- Stage 1: **TotalSegmentator** (robust, clinical-grade) for pancreas detection
- Stage 2: Custom U-Net (128×128) for tumor detection

**Results:** Saved to `test_results_totalseg/`

### 🔄 Comparison Tools
- `compare_methods.py` - Visual comparison of both methods side-by-side

---

## 🚀 Quick Start

### Option 1: Original Method (Already Working)

```bash
cd Testing_Model
python test_pancreas_detection.py
```

**Pros:** Fast, uses your trained models  
**Cons:** Limited to training data distribution

### Option 2: Hybrid Method (NEW - Recommended)

**Step 1: Install TotalSegmentator**
```bash
# Windows
install_totalseg.bat

# Or manually
pip install TotalSegmentator
```

**Step 2: Run hybrid test**
```bash
python test_pancreas_detection_totalseg.py
```

**Pros:** Robust pancreas detection, better generalization, clinical-grade  
**Cons:** Slower on CPU (~5-8 min), needs model download on first run (~1.5GB)

### Compare Both Methods

```bash
# First run both methods
python test_pancreas_detection.py
python test_pancreas_detection_totalseg.py

# Then compare results
python compare_methods.py
```

---

## 📊 Results Comparison

### Your Test Results (`pancreas_001.nii.gz`)

| Metric | Original Method | Hybrid Method |
|--------|----------------|---------------|
| **Slices with Pancreas** | 47/110 (42.7%) | Will vary |
| **Slices with Tumor** | 39 slices | Will vary |
| **Processing Time (CPU)** | ~2 minutes | ~5-8 minutes |
| **Pancreas Model** | Custom U-Net | TotalSegmentator |
| **Tumor Model** | Custom U-Net | Custom U-Net (same) |

---

## 🎯 Why Use the Hybrid Method?

### TotalSegmentator Advantages:

1. **Robustness**: Trained on 1000+ diverse CT scans
   - Different scanners, protocols, patient populations
   - Handles various image qualities and artifacts

2. **Clinical Validation**: 
   - Published in peer-reviewed journals
   - Used in medical research worldwide
   - 100+ anatomical structures, not just pancreas

3. **Maintained & Updated**:
   - Active GitHub repository: https://github.com/wasserth/TotalSegmentator
   - Regular improvements and bug fixes
   - Community support

4. **Better Generalization**:
   - Works on CT scans from different hospitals
   - Handles edge cases your training data may not cover
   - More reliable in production environments

### Your Custom Tumor Model Advantages:

1. **Specialized**: Trained specifically for pancreatic tumors
2. **Domain Knowledge**: Captures tumor-specific features
3. **Optimized**: Fine-tuned for your use case

### The Hybrid = Best of Both Worlds! 🎉

---

## 📖 Detailed Documentation

For comprehensive information about the hybrid method, see:
- **[README_TOTALSEG.md](README_TOTALSEG.md)** - Full documentation
- **[TotalSegmentator GitHub](https://github.com/wasserth/TotalSegmentator)** - Official repository

---

## 🔧 Troubleshooting

### TotalSegmentator Installation Issues

**Problem:** `ModuleNotFoundError: No module named 'totalsegmentator'`
```bash
pip install TotalSegmentator
```

**Problem:** First run is very slow
- TotalSegmentator downloads models (~1.5GB) on first use
- Subsequent runs are much faster

**Problem:** Out of memory on CPU
```python
# In test_pancreas_detection_totalseg.py, line ~80
totalsegmentator(..., fast=True)  # Use faster, lighter model
```

### GPU Acceleration (Optional)

For **30x faster** processing, install PyTorch with CUDA:

```bash
# Check if you have NVIDIA GPU
nvidia-smi

# Install PyTorch with CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Then in script, change device="cpu" to device="gpu"
```

---

## 📂 Output Structure

### `test_results/` (Original Method)
```
test_results/
├── slice_009_PANCREAS_AND_TUMOR.png
├── slice_010_PANCREAS_ONLY.png
├── ...
└── summary_visualization.png
```

### `test_results_totalseg/` (Hybrid Method)
```
test_results_totalseg/
├── slice_009_PANCREAS_AND_TUMOR.png
├── slice_010_PANCREAS_ONLY.png
├── ...
└── summary_visualization.png
```

### `method_comparison.png` (After running compare_methods.py)
Side-by-side comparison showing differences between methods.

---

## 🎨 Visualization Legend

Both methods use the same color scheme:
- **Cyan contours** 🩵 = Pancreas boundary
- **Red contours** ❤️ = Tumor regions

The difference is in **pancreas detection**:
- Original: Your custom U-Net
- Hybrid: TotalSegmentator (more robust)

---

## 📝 Notes

1. **Test Data**: Currently uses `Testset/pancreas_001.nii.gz`
   - To test other files, edit `TEST_FILE` variable in scripts

2. **Model Requirements**:
   - Original: Needs `../Model/unet_best_pancreas.keras` and `unet_best_tumor.keras`
   - Hybrid: Only needs `../Model/unet_best_tumor.keras` (TotalSegmentator downloads automatically)

3. **Processing Time**:
   - CPU: Original ~2 min, Hybrid ~5-8 min
   - GPU: Hybrid can be faster (~30 sec with CUDA)

---

## 🔬 For Researchers

If you use the hybrid approach in your research, please cite:

**TotalSegmentator:**
```
Wasserthal et al. "TotalSegmentator: robust segmentation of 104 
anatomical structures in CT images." 
Radiology: Artificial Intelligence, 2023.
```

**Your Custom Tumor Model:**
```
[Your citation for the custom pancreatic tumor detection model]
```

---

## 🤝 Support

- **TotalSegmentator Issues**: https://github.com/wasserth/TotalSegmentator/issues
- **Custom Model Issues**: Contact your model development team
- **This Testing Suite**: Check this README and documentation files

---

## 📈 Future Improvements

Potential enhancements:
- [ ] Batch processing for multiple CT scans
- [ ] GPU auto-detection and optimization
- [ ] Web interface for easy testing
- [ ] ROC curve analysis comparing both methods
- [ ] Integration with Flutter app for live comparison

---

**🎯 Recommendation:** Start with the **hybrid method** for more robust pancreas detection while maintaining your specialized tumor detection capabilities!
