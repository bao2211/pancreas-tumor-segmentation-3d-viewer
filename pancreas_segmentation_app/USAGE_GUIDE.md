# NIfTI CT Scan Analysis - Quick Start Guide

## ✅ Your App is Now Running!

The Flutter app is successfully running with the new **NIfTI Scan** feature for two-stage pancreas and tumor detection.

## 🚀 Features

### 1. **Single Image Mode** (Original Feature)
- Analyze individual CT scan images (PNG, JPG, TIFF, etc.)
- Quick segmentation for single slices

### 2. **NIfTI Scan Mode** (NEW!)
- Load complete .nii or .nii.gz files
- View all CT slices from the 3D volume
- Two-stage detection:
  1. **Stage 1**: Pancreas segmentation (256x256)
  2. **Stage 2**: Tumor detection within pancreas ROI (128x128)
- Real-time visualization with color-coded overlays
- Comprehensive statistics and tumor alerts

## 📖 How to Use NIfTI Scan Mode

### Step 1: Switch to NIfTI Mode
- Click on **"NIfTI Scan"** in the left navigation rail

### Step 2: Load a NIfTI File
1. Click the **"Load NIfTI File"** button (floating action button)
2. Select a `.nii` or `.nii.gz` file from your computer
3. Wait for the file to load (5-30 seconds depending on file size)
4. All CT slices will be extracted and displayed

### Step 3: Browse CT Slices
- **Slider**: Drag to quickly jump between slices
- **Arrow buttons**: Navigate one slice at a time
- **Slice list**: Click on any slice in the left panel
- **Zoom**: Use mouse scroll or pinch gesture to zoom in/out

### Step 4: Run Scan
1. Click **"Scan All Slices"** button
2. The system will process each slice:
   - First, detect pancreas (cyan contour)
   - Then, detect tumors within pancreas (red contour)
3. Watch the progress bar
4. Review results in the left panel

### Step 5: Review Results
- **Statistics Panel**: Shows:
  - Total number of slices
  - Slices with pancreas detected
  - Slices with tumor detected
- **Slice Status Icons**:
  - ⚠️ Orange warning: Tumor detected
  - ✓ Green check: Pancreas only
  - ○ Gray circle: No pancreas
- **Overlay Legend**:
  - **Cyan contour**: Pancreas boundary
  - **Red contour**: Tumor boundary

### Tumor Detection Alert
If tumors are detected, you'll see an alert:
```
⚠️ PHÁT HIỆN VÙNG NGHI NGỜ KHỐI U TUYẾN TỤY

Số slice phát hiện u: X

➡ Khuyến nghị: Bác sĩ nên đánh giá lại trên hình ảnh gốc.
➡ Kết quả mang tính hỗ trợ, không thay thế chẩn đoán lâm sàng.
```

## 🎨 Visual Guide

### Color Coding
- **Black background**: CT slice view
- **Cyan/Yellow contours**: Pancreas region
- **Red contours**: Tumor region
- **Orange icons**: Tumor alert
- **Green icons**: Pancreas detected
- **Gray icons**: Nothing detected

### Navigation
```
┌─────────────────┬──────────────────────┐
│  Slice List     │   Slice Viewer       │
│                 │                      │
│  ⚠️ Slice 15    │   [CT Image with    │
│  ✓ Slice 16     │    color overlays]   │
│  ○ Slice 17     │                      │
│                 │   ◀ Slider Controls ▶│
└─────────────────┴──────────────────────┘
```

## 🔬 Technical Details

### Image Preprocessing (Matching Training Pipeline)

**For Pancreas Model:**
```python
1. HU windowing: clip to [-128, 127]
2. Normalize: (value + 128) / 255.0
3. Resize: to 256x256
4. Format: (1, 256, 256, 1) - grayscale
```

**For Tumor Model:**
```python
1. Crop ROI: bounding box of detected pancreas
2. Resize: to 128x128  
3. Format: (1, 128, 128, 1) - grayscale
```

### Model Pipeline

```
CT Slice (raw HU values)
     ↓
[HU Window + Normalize]
     ↓
Pancreas Model (256x256)
     ↓
Pancreas Mask
     ↓
[Crop ROI + Resize]
     ↓
Tumor Model (128x128)
     ↓
Tumor Mask
     ↓
[Resize to original + Overlay]
```

## 🐛 Troubleshooting

### "Server not ready"
**Solution:**
1. Make sure the Python inference server is running
2. Check terminal for: `✓ Server running at http://localhost:8765`
3. If needed, restart: `python nii_inference_server.py`

### "Failed to load file"
**Possible causes:**
- File is not a valid .nii/.nii.gz file
- File is corrupted
- Server timeout (very large files)

**Solution:**
- Verify file format
- Try a smaller file first
- Check server logs for errors

### "Models not loaded"
**Solution:**
1. Verify model files exist in `Model/` folder:
   - `unet_best_pancreas.keras`
   - `unet_best_tumor.keras`
2. Check server startup messages
3. Run: `python test_setup.py`

### Slow performance
**Tips:**
- Close other applications
- Process smaller volumes first
- Use release build: `flutter run -d windows --release`

## 📊 Sample Test Data

To test the application, you can use:
- Sample .nii files from the `imagesTs` folder in your data
- Any medical CT scan in NIfTI format (.nii or .nii.gz)

## ⚕️ Medical Disclaimer

**IMPORTANT NOTES:**
1. This is a **research and educational tool**
2. Results are for **assistance only**
3. **NOT** a substitute for professional medical diagnosis
4. Always have qualified medical professionals review images
5. Clinical decisions should be made by licensed healthcare providers
6. This tool has not been clinically validated or FDA approved

## 🔧 Server Management

### Start Server
```bash
python nii_inference_server.py
```

### Stop Server
- Press `Ctrl+C` in the server terminal
- Or close the server window

### Change Server Port
Edit `nii_inference_server.py`:
```python
PORT = 8765  # Change this line
```

Then update in Flutter app: Settings → Server URL

## 💡 Tips for Best Results

1. **Slice Selection**: Focus on slices where pancreas is visible (usually middle sections)
2. **Zoom In**: Use zoom to examine detailed regions
3. **Compare Slices**: Navigate between adjacent slices to verify findings
4. **Check Statistics**: Review the summary before making conclusions
5. **Multiple Scans**: Run analysis on multiple patients/scans for comparison

## 📝 Keyboard Shortcuts (coming soon)
- `←/→`: Previous/Next slice
- `Home`: First slice
- `End`: Last slice
- `Space`: Toggle overlay
- `+/-`: Zoom in/out

## 🆘 Support

If you encounter issues:
1. Check the server terminal for error messages
2. Run `python test_setup.py` to verify setup
3. Review the `NII_SCAN_README.md` for detailed documentation
4. Check that models match the expected format and input sizes

---

**Version**: 1.0.0  
**Last Updated**: January 15, 2026  
**Models Required**: unet_best_pancreas.keras (256x256), unet_best_tumor.keras (128x128)
