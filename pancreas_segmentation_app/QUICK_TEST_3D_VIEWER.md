# 3D Viewer Quick Test Checklist

## ✅ Pre-Test Setup

- [ ] Python server is running on port 8765
- [ ] Both model files exist: `unet_best_pancreas.keras` and `unet_best_tumor.keras`
- [ ] Dependencies installed: `pip install scikit-image trimesh` (if not already)
- [ ] Flutter app is compiled and running

## ✅ Testing Steps

1. **Load NIfTI File**
   - [ ] File loads successfully
   - [ ] Shows total number of slices
   - [ ] No error messages

2. **Scan All Slices**
   - [ ] Progress bar advances
   - [ ] Shows slice count (e.g., "25/50")
   - [ ] Completes to 100%
   - [ ] At least some slices detect pancreas (check statistics)

3. **Check Python Server Logs**
   Look for this message during scanning:
   - [ ] `[INFO] Initialized 3D mask accumulation: shape=(256, 256, X)`

4. **Click "3D Viewer" Button**
   - [ ] Loading dialog appears
   - [ ] Check Python server for these messages:
     - [ ] `[INFO] Generating 3D meshes from segmentation masks...`
     - [ ] `[OK] Pancreas mesh: XXX vertices, YYY faces`
     - [ ] `[OK] GLB generated: XXXXX bytes`
   - [ ] New browser window opens

5. **In 3D Viewer Window (Press F12)**
   Check browser console for:
   - [ ] `✅ WebGL 2.0 renderer initialized`
   - [ ] `✅ Three.js initialized`
   - [ ] `Received model data via postMessage`
   - [ ] `✅ GLB loaded successfully!`
   - [ ] `Found mesh: pancreas` or `Found mesh: tumor`
   - [ ] `Total meshes found: X` (where X > 0)
   - [ ] `✅ Model centered at origin`

6. **Visual Check**
   - [ ] You see 3D mesh(es) in the viewer
   - [ ] Pancreas is cyan/turquoise color
   - [ ] Tumor is red color (if detected)
   - [ ] Can rotate with mouse (left-click drag)
   - [ ] Can zoom with scroll wheel
   - [ ] Can pan with right-click drag

## ❌ If Something Fails

### No "Initialized 3D mask accumulation" message
**Problem**: Masks aren't being accumulated during scan.
**Action**: 
1. Check that scan actually completed
2. Verify at least one slice has pancreas detected
3. Restart Python server

### "No scan data available" error
**Problem**: You didn't scan before opening 3D viewer.
**Action**: Click "Scan All Slices" first, wait for completion.

### "No meshes found in GLB file"
**Problem**: Marching cubes couldn't generate geometry.
**Action**: 
1. Check Python errors in console
2. Verify masks have non-zero pixels
3. Try a different NIfTI file

### Viewer window opens but stays on loading screen
**Problem**: Model data not being received.
**Action**:
1. Check Flutter console for errors
2. Verify browser console (F12) for JavaScript errors
3. Look for "No modelData in message!" error

### Model loads but you see nothing
**Problem**: Camera or mesh positioning issue.
**Action**:
1. Try clicking "Reset Camera" button
2. Try zooming out (scroll wheel)
3. Check browser console for "Model has zero size" or "Invalid bounding box"

## 📊 Success Criteria

**You should see**:
- ✅ 3D visualization window opens
- ✅ Pancreas mesh visible (cyan color)
- ✅ Tumor mesh visible (red color) - if tumor was detected
- ✅ Smooth rotation and zooming
- ✅ No error messages in console
- ✅ Controls work (auto-rotate, light slider, etc.)

## 🔍 Debug Files

If you need more detailed help, check:
- `DEBUG_3D_VIEWER.md` - Full debugging guide
- `FIX_SUMMARY_3D_VIEWER.md` - What was fixed and why

## 📝 Notes

- First load might be slower as models initialize
- Larger scans (more slices) = larger GLB files = longer load times
- If you have 100+ slices, mesh generation can take 30-60 seconds
- WebGL 2.0 is required - use recent Chrome, Edge, or Firefox
