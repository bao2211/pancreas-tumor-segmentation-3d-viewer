"""
Test script for two-stage pancreas and tumor detection
Based on 14_01_TEST_phuong_an_1_tumor_pancreas notebook
"""
import os
import sys
import numpy as np
import cv2
import matplotlib.pyplot as plt
import nibabel as nib
import tensorflow as tf
from pathlib import Path

# Suppress TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU

# Paths
TEST_FILE = "Testset/pancreas_001.nii.gz"
MODEL_DIR = "Model"
PANCREAS_MODEL_PATH = os.path.join(MODEL_DIR, "unet_best_pancreas.keras")
TUMOR_MODEL_PATH = os.path.join(MODEL_DIR, "unet_best_tumor.keras")
OUTPUT_DIR = "test_results"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*60)
print("Two-Stage Pancreas & Tumor Detection Test")
print("="*60)

# ===== PREPROCESSING FUNCTIONS (from notebook) =====
def hu_window(img):
    """HU windowing: clip to [-128, 127] and normalize to [0, 1]"""
    img = np.clip(img, -128, 127)
    img = (img + 128) / 255.0
    return img.astype(np.float32)

def prep_pancreas(img):
    """Prepare image for pancreas model (256x256)"""
    img = hu_window(img)
    img = cv2.resize(img, (256, 256))
    return img[..., None]

def prep_tumor(img):
    """Prepare image for tumor model (128x128)"""
    img = cv2.resize(img, (128, 128))
    return img[..., None]

# ===== LOAD MODELS =====
print("\n[1] Loading models...")
try:
    pancreas_model = tf.keras.models.load_model(PANCREAS_MODEL_PATH, compile=False)
    print(f"[OK] Pancreas model loaded: {pancreas_model.input_shape}")
    
    tumor_model = tf.keras.models.load_model(TUMOR_MODEL_PATH, compile=False)
    print(f"[OK] Tumor model loaded: {tumor_model.input_shape}")
except Exception as e:
    print(f"[ERROR] Error loading models: {e}")
    sys.exit(1)

# ===== LOAD TEST FILE =====
print(f"\n[2] Loading test file: {TEST_FILE}")
try:
    nii = nib.load(TEST_FILE)
    vol = nii.get_fdata()
    print(f"[OK] Loaded volume: shape={vol.shape}, dtype={vol.dtype}")
    print(f"     Min/Max HU values: {vol.min():.1f} / {vol.max():.1f}")
except Exception as e:
    print(f"[ERROR] Error loading file: {e}")
    sys.exit(1)

# ===== PROCESS ALL SLICES =====
print(f"\n[3] Processing {vol.shape[2]} slices...")
pancreas_masks = []
tumor_masks = []
cnt_pancreas = 0
cnt_tumor = 0

for z in range(vol.shape[2]):
    if (z + 1) % 10 == 0:
        print(f"  Processing slice {z+1}/{vol.shape[2]}...")
    
    raw = vol[:, :, z]
    
    # ===== STAGE 1: PANCREAS DETECTION =====
    x = prep_pancreas(raw)[None, ...]
    pred = pancreas_model.predict(x, verbose=0)[0]
    mask_p = np.argmax(pred, -1).astype(np.uint8)
    
    if np.any(mask_p == 1):
        cnt_pancreas += 1
    
    pancreas_masks.append(mask_p)
    
    # ===== STAGE 2: TUMOR DETECTION =====
    ys, xs = np.where(mask_p == 1)
    if len(xs) == 0:
        # No pancreas detected
        tumor_masks.append(np.zeros((512, 512), dtype=np.uint8))
        continue
    
    y1, y2 = ys.min(), ys.max()
    x1, x2 = xs.min(), xs.max()
    
    # Get ROI from normalized image
    img_norm = prep_pancreas(raw)[..., 0]
    roi = img_norm[y1:y2, x1:x2]
    
    # Tumor detection on ROI
    x_t = prep_tumor(roi)[None, ...]
    pred_t = tumor_model.predict(x_t, verbose=0)[0]
    mask_t = np.argmax(pred_t, -1).astype(np.uint8)
    
    # Resize tumor mask back to 256x256
    mask_tumor_roi = cv2.resize(
        mask_t, 
        (x2 - x1, y2 - y1),
        interpolation=cv2.INTER_NEAREST
    )
    
    # Map to 512x512
    m_full = np.zeros((512, 512), dtype=np.uint8)
    
    # Scale coordinates from 256 to 512
    scale = 512 / 256
    y1_full = int(y1 * scale)
    y2_full = int(y2 * scale)
    x1_full = int(x1 * scale)
    x2_full = int(x2 * scale)
    
    # Resize to full resolution
    mask_tumor_full_roi = cv2.resize(
        mask_tumor_roi,
        (x2_full - x1_full, y2_full - y1_full),
        interpolation=cv2.INTER_NEAREST
    )
    
    m_full[y1_full:y2_full, x1_full:x2_full] = mask_tumor_full_roi
    
    if np.any(mask_t == 1):
        cnt_tumor += 1
    
    tumor_masks.append(m_full)

print(f"[OK] Processing complete!")

# ===== STATISTICS =====
print(f"\n[4] Statistical Analysis")
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
print(f"\n[5] Generating overlay images...")

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
        # Resize to match original 512x512
        p_full = cv2.resize(p, (512, 512), interpolation=cv2.INTER_NEAREST)
        cnts, _ = cv2.findContours(
            p_full, cv2.RETR_EXTERNAL,
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
print(f"\n[6] Creating summary visualization...")

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
            p_full = cv2.resize(p, (512, 512), interpolation=cv2.INTER_NEAREST)
            cnts, _ = cv2.findContours(p_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_rgb, cnts, -1, (0, 255, 255), 2)
        
        # Tumor
        t = tumor_masks[sl]
        if np.any(t == 1):
            cnts, _ = cv2.findContours(t, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_rgb, cnts, -1, (255, 0, 0), 2)
        
        axes[1, idx].imshow(img_rgb)
        axes[1, idx].set_title(f'Slice {sl} - Overlay')
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
print(f"Slices with pancreas: {cnt_pancreas}")
print(f"Slices with significant tumor (>={MIN_PIXELS} pixels): {len(valid_tumor_slices)}")

if len(valid_tumor_slices) > 0:
    print("\n[WARNING] RESULT: SUSPICIOUS TUMOR REGIONS DETECTED")
    print("          Clinical review recommended")
    print("          This is an AI-assisted analysis, not a clinical diagnosis")
else:
    print("\n[OK] RESULT: NO SIGNIFICANT TUMOR DETECTED")
    print("     Clinical correlation still advised")

print("="*60)
print("\nTest complete! Check the 'test_results' folder for detailed outputs.")
