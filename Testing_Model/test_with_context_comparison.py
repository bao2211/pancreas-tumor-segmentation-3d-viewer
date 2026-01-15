"""
Test script to compare tumor detection with and without context-aware prediction

This script processes a CT scan twice:
1. Without context (baseline)
2. With context-aware prediction (improved)

Then displays side-by-side comparison showing improvements in:
- Tumor continuity across slices
- Noise reduction
- Blob connectivity
"""

import os
import sys
import numpy as np
import nibabel as nib
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

# Force CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

try:
    import tensorflow as tf
    # CPU optimization
    tf.config.threading.set_inter_op_parallelism_threads(4)
    tf.config.threading.set_intra_op_parallelism_threads(4)
except ImportError:
    print("[ERROR] TensorFlow not installed!")
    sys.exit(1)

# ==================== CONFIGURATION ====================
CT_IMAGE_PATH = Path("../Testset/pancreas_001.nii.gz")
PANCREAS_MODEL_PATH = Path("../Model/unet_best_pancreas.keras")
TUMOR_MODEL_PATH = Path("../Model/unet_best_tumor.keras")
OUTPUT_DIR = Path("test_results_context_comparison")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# ==================== PREPROCESSING ====================
def hu_window(img, w_center=-25, w_width=250):
    """Apply HU windowing"""
    lower = w_center - w_width / 2
    upper = w_center + w_width / 2
    img_clipped = np.clip(img, lower, upper)
    img_norm = (img_clipped - lower) / (upper - lower)
    return img_norm

def prep_pancreas(img):
    """Prepare image for pancreas model (256x256)"""
    img_windowed = hu_window(img)
    img_resized = cv2.resize(img_windowed, (256, 256))
    return np.expand_dims(img_resized, axis=-1)

def prep_tumor(img):
    """Prepare image for tumor model (128x128)"""
    img_resized = cv2.resize(img, (128, 128))
    return np.expand_dims(img_resized, axis=-1)

# ==================== CONTEXT SYSTEM ====================
class TumorContext:
    """Context-aware tumor prediction"""
    def __init__(self, context_window=3):
        self.context_window = context_window
        self.history = []
    
    def reset(self):
        self.history = []
    
    def add_prediction(self, slice_idx, tumor_mask):
        if tumor_mask is not None and np.any(tumor_mask == 1):
            ys, xs = np.where(tumor_mask == 1)
            centroid = (np.mean(ys), np.mean(xs))
            self.history.append((slice_idx, tumor_mask.copy(), centroid))
        else:
            self.history.append((slice_idx, None, None))
        
        if len(self.history) > self.context_window:
            self.history.pop(0)
    
    def refine_prediction(self, raw_tumor_mask, slice_idx):
        if raw_tumor_mask is None or not np.any(raw_tumor_mask == 1):
            return raw_tumor_mask
        
        # Apply morphological operations
        refined = self.enforce_connectivity(raw_tumor_mask)
        
        # Apply temporal smoothing if we have history
        if len(self.history) >= 2:
            refined = self.temporal_smoothing(refined, slice_idx)
        
        return refined
    
    def enforce_connectivity(self, tumor_mask):
        """Ensure tumor appears as connected blobs"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        closed = cv2.morphologyEx(tumor_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
        
        if num_labels <= 1:
            return tumor_mask
        
        result = np.zeros_like(tumor_mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= 10:
                result[labels == i] = 1
        
        return result.astype(np.uint8)
    
    def temporal_smoothing(self, current_mask, slice_idx):
        """Apply temporal smoothing using previous slices"""
        if not self.history:
            return current_mask
        
        prev_masks = [mask for idx, mask, _ in self.history if mask is not None]
        if not prev_masks:
            return current_mask
        
        vote_map = current_mask.astype(np.float32) * 2.0
        
        for mask in prev_masks[-2:]:
            if mask.shape != current_mask.shape:
                mask_resized = cv2.resize(mask, (current_mask.shape[1], current_mask.shape[0]),
                                         interpolation=cv2.INTER_NEAREST)
            else:
                mask_resized = mask
            vote_map += mask_resized.astype(np.float32)
        
        smoothed = (vote_map >= 2.0).astype(np.uint8)
        return smoothed

# ==================== DETECTION ====================
def process_slice(slice_data, pancreas_model, tumor_model, use_context=False, context=None):
    """Process single slice"""
    # Pancreas detection
    x_pancreas = prep_pancreas(slice_data)[None, ...]
    pred_pancreas = pancreas_model.predict(x_pancreas, verbose=0)[0]
    mask_pancreas = np.argmax(pred_pancreas, -1).astype(np.uint8)
    
    mask_tumor_full = None
    
    if np.sum(mask_pancreas == 1) > 0:
        # Tumor detection
        ys, xs = np.where(mask_pancreas == 1)
        y1, y2 = ys.min(), ys.max()
        x1, x2 = xs.min(), xs.max()
        
        img_norm = prep_pancreas(slice_data)[..., 0]
        roi = img_norm[y1:y2, x1:x2]
        
        x_tumor = prep_tumor(roi)[None, ...]
        pred_tumor = tumor_model.predict(x_tumor, verbose=0)[0]
        mask_tumor_128 = np.argmax(pred_tumor, -1).astype(np.uint8)
        
        mask_tumor_roi = cv2.resize(mask_tumor_128, (x2 - x1, y2 - y1),
                                    interpolation=cv2.INTER_NEAREST)
        
        mask_tumor_full = np.zeros((256, 256), dtype=np.uint8)
        mask_tumor_full[y1:y2, x1:x2] = mask_tumor_roi
        
        if use_context and context is not None:
            mask_tumor_full = context.refine_prediction(mask_tumor_full, None)
    
    if use_context and context is not None:
        context.add_prediction(None, mask_tumor_full)
    
    return mask_pancreas, mask_tumor_full

# ==================== MAIN ====================
def main():
    print("\n" + "="*70)
    print("CONTEXT-AWARE TUMOR PREDICTION COMPARISON TEST")
    print("="*70)
    
    # Load models
    print("\n[1] Loading models...")
    pancreas_model = tf.keras.models.load_model(PANCREAS_MODEL_PATH)
    tumor_model = tf.keras.models.load_model(TUMOR_MODEL_PATH)
    print("[OK] Models loaded")
    
    # Load CT image
    print(f"\n[2] Loading CT image: {CT_IMAGE_PATH}")
    nii = nib.load(CT_IMAGE_PATH)
    vol = nii.get_fdata()
    print(f"[OK] Volume shape: {vol.shape}")
    
    # Select middle slices for comparison
    z_start = vol.shape[2] // 2 - 5
    z_end = vol.shape[2] // 2 + 5
    num_slices = z_end - z_start
    
    print(f"\n[3] Processing slices {z_start} to {z_end} ({num_slices} slices)")
    
    # Process WITHOUT context
    print("\n[3a] Processing WITHOUT context...")
    results_no_context = []
    for z in range(z_start, z_end):
        slice_data = vol[:, :, z]
        mask_p, mask_t = process_slice(slice_data, pancreas_model, tumor_model, 
                                       use_context=False)
        results_no_context.append((z, mask_p, mask_t))
    
    # Process WITH context
    print("[3b] Processing WITH context...")
    context = TumorContext(context_window=3)
    results_with_context = []
    for z in range(z_start, z_end):
        slice_data = vol[:, :, z]
        mask_p, mask_t = process_slice(slice_data, pancreas_model, tumor_model,
                                       use_context=True, context=context)
        results_with_context.append((z, mask_p, mask_t))
    
    # Compare results
    print("\n[4] Comparing results...")
    
    # Count differences
    tumor_pixels_no_context = [np.sum(m[2] == 1) if m[2] is not None else 0 
                               for m in results_no_context]
    tumor_pixels_with_context = [np.sum(m[2] == 1) if m[2] is not None else 0 
                                 for m in results_with_context]
    
    print(f"\nSlices with tumor (no context):   {sum(1 for p in tumor_pixels_no_context if p > 10)}")
    print(f"Slices with tumor (with context):  {sum(1 for p in tumor_pixels_with_context if p > 10)}")
    
    # Visualize comparison
    print("\n[5] Creating visualization...")
    
    fig, axes = plt.subplots(3, num_slices, figsize=(20, 8))
    
    for i, z_rel in enumerate(range(num_slices)):
        z = z_start + z_rel
        slice_data = vol[:, :, z]
        
        # Original image
        img = hu_window(slice_data)
        img_resized = cv2.resize(img, (256, 256))
        axes[0, i].imshow(img_resized, cmap='gray')
        axes[0, i].set_title(f'Slice {z}', fontsize=8)
        axes[0, i].axis('off')
        
        # Without context
        _, _, mask_t_no = results_no_context[z_rel]
        img_no_context = cv2.cvtColor((img_resized * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        if mask_t_no is not None and np.any(mask_t_no == 1):
            contours, _ = cv2.findContours(mask_t_no, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_no_context, contours, -1, (255, 0, 0), 2)
        axes[1, i].imshow(img_no_context)
        axes[1, i].set_title(f'{tumor_pixels_no_context[z_rel]}px', fontsize=8)
        axes[1, i].axis('off')
        
        # With context
        _, _, mask_t_with = results_with_context[z_rel]
        img_with_context = cv2.cvtColor((img_resized * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        if mask_t_with is not None and np.any(mask_t_with == 1):
            contours, _ = cv2.findContours(mask_t_with, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_with_context, contours, -1, (0, 255, 0), 2)
        axes[2, i].imshow(img_with_context)
        axes[2, i].set_title(f'{tumor_pixels_with_context[z_rel]}px', fontsize=8)
        axes[2, i].axis('off')
    
    axes[0, 0].set_ylabel('Original', fontsize=10)
    axes[1, 0].set_ylabel('No Context (Red)', fontsize=10)
    axes[2, 0].set_ylabel('With Context (Green)', fontsize=10)
    
    plt.suptitle('Context-Aware Tumor Prediction Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'context_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"[OK] Saved comparison to: {output_path}")
    
    # Calculate continuity score
    def calc_continuity(pixel_counts):
        """Calculate how continuous tumor presence is"""
        has_tumor = [1 if p > 10 else 0 for p in pixel_counts]
        if sum(has_tumor) == 0:
            return 0.0
        
        # Count transitions (tumor -> no tumor or vice versa)
        transitions = sum(1 for i in range(len(has_tumor) - 1) 
                         if has_tumor[i] != has_tumor[i + 1])
        
        # Fewer transitions = better continuity
        continuity = 1.0 - (transitions / len(has_tumor))
        return continuity
    
    continuity_no_context = calc_continuity(tumor_pixels_no_context)
    continuity_with_context = calc_continuity(tumor_pixels_with_context)
    
    print(f"\nContinuity score (no context):    {continuity_no_context:.2f}")
    print(f"Continuity score (with context):   {continuity_with_context:.2f}")
    print(f"Improvement: {(continuity_with_context - continuity_no_context) * 100:+.1f}%")
    
    print("\n" + "="*70)
    print("COMPARISON COMPLETE!")
    print("="*70)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("Open context_comparison.png to see visual comparison")

if __name__ == '__main__':
    main()
