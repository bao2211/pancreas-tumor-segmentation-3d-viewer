# NIfTI CT Scan Analysis - Setup Guide

## Overview

This application now supports two modes:
1. **Single Image Mode**: Analyze individual CT scan images (PNG, JPG, etc.)
2. **NIfTI Scan Mode**: Load complete .nii/.nii.gz files and perform two-stage pancreas & tumor detection

## Prerequisites

### Python Dependencies

Install the required Python packages for the inference server:

```bash
pip install tensorflow numpy opencv-python pillow nibabel
```

**Important**: The `nibabel` package is required for .nii file support.

### Models Required

Place these models in the `Model/` folder:
- `unet_best_pancreas.keras` - Pancreas segmentation model (256x256 input)
- `unet_best_tumor.keras` - Tumor detection model (128x128 input)

## Running the Application

### Step 1: Start the Inference Server

For NIfTI file support, use the new server:

```bash
cd pancreas_segmentation_app
python nii_inference_server.py
```

The server will start on `http://localhost:8765`

**Note**: Make sure both model files are found by the server. Check the console output.

### Step 2: Run the Flutter App

Using the virtual drive (to avoid path length issues):

```bash
P:
cd pancreas_segmentation_app
flutter run -d windows
```

Or from the root directory:

```bash
subst P: "C:\Users\Admin\Documents\School\AI\MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection"
cd P:\pancreas_segmentation_app
flutter run -d windows
```

## Using the NIfTI Scan Feature

1. **Select NIfTI Mode**: Click on "NIfTI Scan" in the navigation rail

2. **Load a .nii/.nii.gz file**: Click "Load NIfTI File" button and select your CT scan file

3. **Browse Slices**: 
   - Use the slider or arrow buttons to navigate through slices
   - Click on individual slices in the left panel

4. **Run Analysis**: Click "Scan All Slices" to process the entire volume:
   - Each slice is first analyzed for pancreas detection
   - If pancreas is found, the ROI is extracted and analyzed for tumors
   - Results are displayed with color-coded contours:
     - **Cyan**: Pancreas boundary
     - **Red**: Tumor boundary

5. **Review Results**:
   - View statistics in the left panel
   - Navigate to slices with tumor detection (marked with ⚠️)
   - If tumors are detected, an alert dialog will appear

## Two-Stage Detection Pipeline

The analysis follows the workflow from your notebook:

### Stage 1: Pancreas Detection
```
Input: Raw CT slice (512x512 or original size)
↓
HU Windowing: clip(-128, 127) → normalize to [0,1]
↓
Resize to 256x256
↓
Pancreas Model (unet_best_pancreas.keras)
↓
Output: Pancreas mask (256x256)
```

### Stage 2: Tumor Detection (if pancreas found)
```
Input: Pancreas mask from Stage 1
↓
Crop ROI (bounding box of pancreas)
↓
Resize ROI to 128x128
↓
Tumor Model (unet_best_tumor.keras)
↓
Output: Tumor mask (128x128)
↓
Resize back to original ROI size
↓
Place in full image coordinates
```

## Image Preprocessing

The preprocessing exactly matches your training notebook:

```python
def hu_window(img):
    """HU windowing"""
    img = np.clip(img, -128, 127)
    img = (img + 128) / 255.0
    return img.astype(np.float32)

def prep_pancreas(img):
    """Prepare for pancreas model (256x256)"""
    img = hu_window(img)
    img = cv2.resize(img, (256, 256))
    return img[..., None]

def prep_tumor(img):
    """Prepare for tumor model (128x128)"""
    img = cv2.resize(img, (128, 128))
    return img[..., None]
```

## Troubleshooting

### Server not connecting
- Make sure the Python server is running
- Check the server URL in settings (default: http://localhost:8765)
- Verify firewall settings

### Models not found
- Ensure `unet_best_pancreas.keras` and `unet_best_tumor.keras` are in the `Model/` folder
- Check the server console for the paths it's searching

### nibabel not installed
```bash
pip install nibabel
```

### Path too long error
- Use the virtual drive workaround: `subst P: "your-long-path"`
- Or enable long path support in Windows (requires admin)

## API Endpoints

The `nii_inference_server.py` provides:

- `GET /health` - Check server status and model availability
- `POST /load_nii` - Load .nii/.nii.gz file and extract all slices
- `POST /scan_slice` - Process a single slice through both models

## Performance

- Loading .nii files: ~5-30 seconds depending on size
- Processing per slice: ~0.5-1 second per slice
- Full volume scan: ~30-60 seconds for typical 40-60 slice volume

## Clinical Use Disclaimer

**⚠️ IMPORTANT**: This is a research/educational tool. Results are for assistance only and do not replace professional medical diagnosis. Always have qualified medical professionals review the images and make clinical decisions.
