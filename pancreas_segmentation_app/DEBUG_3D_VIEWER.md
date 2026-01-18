# 3D Viewer Debugging Guide

## Changes Made

### 1. Fixed Model Data Passing (volume_3d_viewer.dart)
**Problem**: JavaScript was hardcoding `'http://localhost:8765/model.glb'` instead of using the data URL from the message.

**Fix**: Updated the message handler to extract and use `event.data.modelData`:
```javascript
const modelDataUrl = event.data.modelData;
loadGLBModel(modelDataUrl);
```

### 2. Enhanced Error Detection and Logging
**Added comprehensive logging to track**:
- Model data URL type and format
- Mesh detection (pancreas vs tumor)
- Material application
- Bounding box validation
- Loading progress with better error messages

### 3. Improved Material Handling
**Changes**:
- Explicitly detect pancreas vs tumor meshes by name
- Apply correct colors: **Tumor = Red (0xff0000)**, **Pancreas = Cyan (0x00ffff)**
- Set proper material properties (opacity, transparency, roughness)
- Enable shadows for better depth perception

## How to Test

### Step 1: Start the Python Server
```powershell
cd pancreas_segmentation_app
python nii_inference_server.py
```

**Expected Output**:
```
[INFO] TensorFlow configured for CPU-only execution
[OK] nibabel available
[INFO] Loading pancreas model from: unet_best_pancreas.keras
[INFO] Loading tumor model from: unet_best_tumor.keras
[OK] Models loaded successfully
Server running on http://localhost:8765
```

### Step 2: Run the Flutter App
```powershell
cd pancreas_segmentation_app
flutter run -d windows
```

Or for web:
```powershell
flutter run -d chrome
```

### Step 3: Load a NIfTI File
1. Click **"Load NIfTI File"**
2. Select a `.nii` or `.nii.gz` CT scan file
3. Wait for it to load (you'll see total slices)

### Step 4: Scan All Slices
1. Click **"Scan All Slices"**
2. Wait for progress bar to reach 100%
3. Check that pancreas and/or tumor are detected

### Step 5: Open 3D Viewer
1. Click **"3D Viewer"** button
2. A new window should open with the 3D visualization

## What to Check in Browser Console

Open the 3D viewer window and press **F12** to open Developer Tools. Look for these messages:

### ✅ Success Indicators:
```
✅ WebGL 2.0 renderer initialized
✅ Three.js initialized
Sent viewerReady signal to parent
Received model data via postMessage
Model data URL type: string
Model data URL starts with: data:model/gltf-binary;base64,
✅ GLB loaded successfully!
Scene children count: 2  (or 1 if only pancreas/tumor)
Found mesh: pancreas
  Applying PANCREAS material (cyan)
Found mesh: tumor
  Applying TUMOR material (red)
Total meshes found: 2
Pancreas mesh found: true
Tumor mesh found: true
✅ Model centered at origin with scale: ...
✅ Model configured and added to scene
```

### ❌ Error Indicators and Solutions:

#### Error: "No modelData in message!"
**Cause**: The data isn't being passed correctly from Flutter to JavaScript.
**Solution**: Check that `volumeViewerData['modelUrl']` exists in the service.

#### Error: "No meshes found in GLB file"
**Cause**: The GLB file is empty or corrupt.
**Check**:
1. Python server logs for mesh generation errors
2. Make sure the scan completed successfully
3. Verify that masks were accumulated (check server logs for "Initialized 3D mask accumulation")

#### Error: "Model has zero size" or "Invalid bounding box"
**Cause**: The mesh geometry is invalid or all vertices are at the same point.
**Check**:
1. Make sure the segmentation masks have actual data (pancreas_pixels > 0)
2. Look for marching cubes errors in Python server logs

#### Error: "Failed to load model"
**Cause**: Data URL is invalid or GLB format is corrupt.
**Check**:
1. Verify base64 encoding is correct
2. Check that trimesh export succeeded on server
3. Look at the exact error message for details

## Python Server Debugging

### Check if Masks are Being Accumulated
Look for these messages in the server terminal:

```
[INFO] Initialized 3D mask accumulation: shape=(256, 256, 50)
```

This should appear when you start scanning slices.

### Check 3D Model Generation
When you click "3D Viewer", look for:

```
[INFO] Generating 3D model...
[INFO] Generating 3D meshes from segmentation masks...
[INFO] Processing pancreas mesh...
[OK] Pancreas mesh: 5234 vertices, 10000 faces
[INFO] Processing tumor mesh...
[OK] Tumor mesh: 1234 vertices, 2468 faces
[INFO] Exporting to glTF format...
[OK] GLB generated: 123456 bytes
```

### Common Python Errors

#### "No scan data available"
**Solution**: Run "Scan All Slices" first before opening 3D viewer.

#### "Failed to generate 3D model. No valid geometry found."
**Cause**: No pancreas or tumor was detected in any slice.
**Solution**: Check that your NIfTI file contains pancreas/tumor data and that the models are working.

#### ImportError for scikit-image or trimesh
**Solution**: 
```powershell
pip install scikit-image trimesh
```

## Manual Testing with Browser

If the automatic viewer isn't working, you can test the GLB file manually:

1. After generating the 3D model, go to: `http://localhost:8765/model.glb`
2. Save the file to disk
3. Use an online GLB viewer: https://gltf-viewer.donmccurdy.com/
4. Drag the saved `.glb` file to check if it's valid

## Expected Behavior

When working correctly, you should see:
- **Cyan semi-transparent mesh** for the pancreas
- **Red opaque mesh** for the tumor(s)
- **Green wireframe box** showing the volume bounds (if volume data is included)
- Smooth rotation with mouse drag
- Zoom with scroll wheel
- Pan with right-click drag

## Camera Controls

- **Left-click + drag**: Rotate
- **Right-click + drag**: Pan  
- **Scroll wheel**: Zoom in/out
- **Auto Rotate checkbox**: Enable automatic rotation
- **Reset Camera button**: Return to default view

## Still Not Working?

Check these final items:

1. **Flutter web compatibility**: Make sure you're using a recent Chrome/Edge browser
2. **CORS issues**: The server already has CORS enabled, but verify it's responding
3. **Port conflicts**: Make sure port 8765 isn't blocked or in use
4. **Model files exist**: Verify `unet_best_pancreas.keras` and `unet_best_tumor.keras` are in the `pancreas_segmentation_app` folder
5. **Python dependencies**: Run `pip list` and verify all required packages are installed

## Get More Help

If you're still having issues, provide:
1. Python server console output (full log)
2. Browser console output from the 3D viewer window (press F12)
3. Screenshot of what you see
4. Operating system and browser version
