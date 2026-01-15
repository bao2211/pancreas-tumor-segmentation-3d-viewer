"""
Hybrid Two-Stage Pancreas & Tumor Detection
Stage 1: TotalSegmentator for robust pancreas detection
Stage 2: Custom U-Net model for tumor detection on pancreas ROI
"""
import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
import nibabel as nib
import tensorflow as tf
import tempfile
import shutil
from pathlib import Path

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU

# Try to import TotalSegmentator
try:
    from totalsegmentator.python_api import totalsegmentator
    HAS_TOTALSEG = True
except ImportError:
    HAS_TOTALSEG = False
    print("[WARNING] TotalSegmentator not installed!")
    print("          Install with: pip install TotalSegmentator")

# Paths
TEST_FILE = "Testset/pancreas_001.nii.gz"
MODEL_DIR = "../Model"
TUMOR_MODEL_PATH = os.path.join(MODEL_DIR, "unet_best_tumor.keras")
OUTPUT_DIR = "test_results_totalseg"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*60)
print("Hybrid Pancreas & Tumor Detection Test")
print("Pancreas: TotalSegmentator (robust pre-trained)")
print("Tumor: Custom U-Net (specialized for pancreatic tumors)")
print("="*60)

# ===== PREPROCESSING FUNCTIONS =====
def hu_window(img):
    """HU windowing: clip to [-128, 127] and normalize to [0, 1]"""
    img = np.clip(img, -128, 127)
    img = (img + 128) / 255.0
    return img.astype(np.float32)

def prep_tumor(img):
    """Prepare image for tumor model (128x128)"""
    img = cv2.resize(img, (128, 128))
    return img[..., None]

# ===== CHECK TOTALSEGMENTATOR =====
print("\n[1] Checking TotalSegmentator...")
if not HAS_TOTALSEG:
    print("[ERROR] TotalSegmentator is required for this script")
    print("        Install with: pip install TotalSegmentator")
    sys.exit(1)
else:
    print("[OK] TotalSegmentator available")

# ===== LOAD TUMOR MODEL =====
print("\n[2] Loading custom tumor detection model...")
try:
    tumor_model = tf.keras.models.load_model(TUMOR_MODEL_PATH, compile=False)
    print(f"[OK] Tumor model loaded: {tumor_model.input_shape}")
except Exception as e:
    print(f"[ERROR] Error loading tumor model: {e}")
    sys.exit(1)

# ===== LOAD TEST FILE =====
print(f"\n[3] Loading test file: {TEST_FILE}")
try:
    nii = nib.load(TEST_FILE)
    vol = nii.get_fdata()
    print(f"[OK] Loaded volume: shape={vol.shape}, dtype={vol.dtype}")
    print(f"     Min/Max HU values: {vol.min():.1f} / {vol.max():.1f}")
except Exception as e:
    print(f"[ERROR] Error loading file: {e}")
    sys.exit(1)

# ===== RUN TOTALSEGMENTATOR FOR PANCREAS =====
print(f"\n[4] Running TotalSegmentator for pancreas detection...")
print("    This may take a few minutes on CPU...")

# Create temporary directory for TotalSegmentator output
temp_dir = tempfile.mkdtemp()
try:
    # TotalSegmentator expects a file path
    input_path = TEST_FILE
    output_path = os.path.join(temp_dir, "segmentation.nii.gz")
    
    # Run TotalSegmentator - only segment organs including pancreas
    print("    [TotalSegmentator] Processing...")
    totalsegmentator(
        input=input_path,
        output=output_path,
        task="total",  # Full body segmentation
        roi_subset=["pancreas"],  # Only segment pancreas for speed
        ml=True,  # Use multilabel output
        fast=False,  # Use accurate model (not fast)
        device="cpu"
    )
    
    # Load the segmentation result
    seg_nii = nib.load(output_path)
    seg_vol = seg_nii.get_fdata()
    
    print(f"[OK] TotalSegmentator complete!")
    print(f"     Segmentation shape: {seg_vol.shape}")
    
    # Extract pancreas mask (label 7 in TotalSegmentator)
    # Create binary masks for each slice
    pancreas_masks = []
    for z in range(vol.shape[2]):
        if z < seg_vol.shape[2]:
            # Get pancreas mask (label 7)
            mask = (seg_vol[:, :, z] == 7).astype(np.uint8)
            pancreas_masks.append(mask)
        else:
            pancreas_masks.append(np.zeros(vol.shape[:2], dtype=np.uint8))
    
    cnt_pancreas = sum(1 for m in pancreas_masks if np.any(m == 1))
    print(f"     Found pancreas in {cnt_pancreas}/{vol.shape[2]} slices")
    
finally:
    # Clean up temporary directory
    shutil.rmtree(temp_dir, ignore_errors=True)

# ===== STAGE 2: TUMOR DETECTION ON PANCREAS ROI =====
print(f"\n[5] Running custom tumor detection on pancreas regions...")
tumor_masks = []
cnt_tumor = 0

for z in range(vol.shape[2]):
    if (z + 1) % 20 == 0:
        print(f"    Processing slice {z+1}/{vol.shape[2]}...")
    
    mask_p = pancreas_masks[z]
    raw = vol[:, :, z]
    
    # Check if pancreas exists in this slice
    ys, xs = np.where(mask_p == 1)
    if len(xs) == 0:
        # No pancreas detected
        tumor_masks.append(np.zeros(vol.shape[:2], dtype=np.uint8))
        continue
    
    # Get bounding box of pancreas
    y1, y2 = ys.min(), ys.max()
    x1, x2 = xs.min(), xs.max()
    
    # Extract ROI from original image
    roi = raw[y1:y2, x1:x2]
    
    # Normalize ROI for tumor model
    roi_norm = hu_window(roi)
    
    # Prepare for tumor model (128x128)
    x_t = prep_tumor(roi_norm)[None, ...]
    pred_t = tumor_model.predict(x_t, verbose=0)[0]
    mask_t = np.argmax(pred_t, -1).astype(np.uint8)
    
    # Resize tumor mask back to ROI size
    mask_tumor_roi = cv2.resize(
        mask_t,
        (x2 - x1, y2 - y1),
        interpolation=cv2.INTER_NEAREST
    )
    
    # Map to full image size
    m_full = np.zeros(vol.shape[:2], dtype=np.uint8)
    m_full[y1:y2, x1:x2] = mask_tumor_roi
    
    if np.any(mask_t == 1):
        cnt_tumor += 1
    
    tumor_masks.append(m_full)

print(f"[OK] Tumor detection complete!")

# ===== STATISTICS =====
print(f"\n[6] Statistical Analysis")
MIN_PIXELS = 10

valid_tumor_slices = []
for i, m in enumerate(tumor_masks):
    area = np.sum(m == 1)
    if area >= MIN_PIXELS:
        valid_tumor_slices.append((i, area))

print("="*60)
print(f"SLICES WITH PANCREAS: {cnt_pancreas}/{vol.shape[2]} ({cnt_pancreas/vol.shape[2]*100:.1f}%)")
print(f"SLICES WITH TUMOR (>={MIN_PIXELS} pixels): {len(valid_tumor_slices)}")
print("="*60)

if len(valid_tumor_slices) > 0:
    print("\n[WARNING] TUMOR DETECTED IN FOLLOWING SLICES:")
    for sl, area in valid_tumor_slices:
        print(f"          Slice {sl:03d} | Tumor pixels = {int(area)}")
else:
    print("\n[OK] NO SIGNIFICANT TUMOR DETECTED")

# ===== SAVE OVERLAYS =====
print(f"\n[7] Generating overlay images...")

for z in range(vol.shape[2]):
    # Only save slices with pancreas
    if np.sum(pancreas_masks[z]) == 0:
        continue
    
    # Create overlay
    img = hu_window(vol[:, :, z])
    img_rgb = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
    
    has_pancreas = False
    has_tumor = False
    
    # Draw pancreas contours (cyan)
    p = pancreas_masks[z]
    if np.any(p == 1):
        cnts, _ = cv2.findContours(
            p, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(img_rgb, cnts, -1, (0, 255, 255), 2)  # Cyan
        has_pancreas = True
    
    # Draw tumor contours (red)
    t = tumor_masks[z]
    if np.any(t == 1):
        cnts, _ = cv2.findContours(
            t.astype(np.uint8), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(img_rgb, cnts, -1, (255, 0, 0), 2)  # Red
        has_tumor = True
    
    # Status
    if has_pancreas and has_tumor:
        status = "PANCREAS_AND_TUMOR"
    elif has_pancreas:
        status = "PANCREAS_ONLY"
    else:
        status = "NONE"
    
    # Save image
    output_path = os.path.join(OUTPUT_DIR, f"slice_{z:03d}_{status}.png")
    cv2.imwrite(output_path, cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))

print(f"[OK] Overlay images saved to: {OUTPUT_DIR}/")

# ===== GENERATE SUMMARY VISUALIZATION =====
print(f"\n[8] Creating summary visualization...")

# Select representative slices
if len(valid_tumor_slices) > 0:
    # Show slices with tumors
    sample_slices = [sl for sl, _ in valid_tumor_slices[:6]]
else:
    # Show slices with pancreas
    sample_slices = [i for i, m in enumerate(pancreas_masks) if np.any(m == 1)][:6]

if len(sample_slices) > 0:
    n_samples = min(6, len(sample_slices))
    fig, axes = plt.subplots(2, n_samples, figsize=(4*n_samples, 8))
    
    if n_samples == 1:
        axes = axes.reshape(2, 1)
    
    for idx, sl in enumerate(sample_slices[:n_samples]):
        # Original slice
        axes[0, idx].imshow(vol[:, :, sl], cmap='gray')
        axes[0, idx].set_title(f'Slice {sl} - Original')
        axes[0, idx].axis('off')
        
        # Overlay
        img = hu_window(vol[:, :, sl])
        img_rgb = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        
        # Pancreas
        p = pancreas_masks[sl]
        if np.any(p == 1):
            cnts, _ = cv2.findContours(p, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_rgb, cnts, -1, (0, 255, 255), 2)
        
        # Tumor
        t = tumor_masks[sl]
        if np.any(t == 1):
            cnts, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_rgb, cnts, -1, (255, 0, 0), 2)
        
        axes[1, idx].imshow(img_rgb)
        axes[1, idx].set_title(f'Slice {sl} - Overlay\n(TotalSeg + Custom)')
        axes[1, idx].axis('off')
    
    plt.tight_layout()
    summary_path = os.path.join(OUTPUT_DIR, "summary_visualization.png")
    plt.savefig(summary_path, dpi=150, bbox_inches='tight')
    print(f"[OK] Summary saved to: {summary_path}")
    plt.close()

# ===== FINAL REPORT =====
print("\n" + "="*60)
print("FINAL CLINICAL REPORT")
print("="*60)
print(f"File: {TEST_FILE}")
print(f"Volume shape: {vol.shape}")
print(f"Total slices: {vol.shape[2]}")
print(f"")
print(f"PANCREAS DETECTION:")
print(f"  Method: TotalSegmentator (pre-trained, robust)")
print(f"  Slices with pancreas: {cnt_pancreas}")
print(f"")
print(f"TUMOR DETECTION:")
print(f"  Method: Custom U-Net (specialized for pancreatic tumors)")
print(f"  Slices with significant tumor (>={MIN_PIXELS} pixels): {len(valid_tumor_slices)}")

if len(valid_tumor_slices) > 0:
    print("\n[WARNING] RESULT: SUSPICIOUS TUMOR REGIONS DETECTED")
    print("          Clinical review recommended")
    print("          This is a hybrid AI-assisted analysis:")
    print("          - Pancreas segmentation: TotalSegmentator")
    print("          - Tumor detection: Custom specialized model")
else:
    print("\n[OK] RESULT: NO SIGNIFICANT TUMOR DETECTED")
    print("     Clinical correlation still advised")

print("="*60)
print(f"\nTest complete! Check '{OUTPUT_DIR}/' for detailed outputs.")
print("\nHybrid Approach Benefits:")
print("  + TotalSegmentator: Robust, well-tested pancreas segmentation")
print("  + Custom Model: Specialized tumor detection on pancreatic tissue")
