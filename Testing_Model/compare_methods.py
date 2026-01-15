"""
Compare Original U-Net vs Hybrid TotalSegmentator approach
Shows side-by-side comparison of pancreas detection methods
"""
import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

print("="*60)
print("Method Comparison Visualizer")
print("="*60)

# Check if both result folders exist
original_dir = "test_results"
hybrid_dir = "test_results_totalseg"

if not os.path.exists(original_dir):
    print(f"[ERROR] Original results not found: {original_dir}")
    print("        Run: python test_pancreas_detection.py")
    sys.exit(1)

if not os.path.exists(hybrid_dir):
    print(f"[ERROR] Hybrid results not found: {hybrid_dir}")
    print("        Run: python test_pancreas_detection_totalseg.py")
    sys.exit(1)

print(f"[OK] Found both result directories")
print(f"     Original: {original_dir}")
print(f"     Hybrid: {hybrid_dir}")

# Get list of slices with tumors from both methods
original_files = sorted([f for f in os.listdir(original_dir) if "TUMOR" in f and f.endswith(".png")])
hybrid_files = sorted([f for f in os.listdir(hybrid_dir) if "TUMOR" in f and f.endswith(".png")])

print(f"\n[INFO] Original method: {len(original_files)} slices with tumors")
print(f"[INFO] Hybrid method: {len(hybrid_files)} slices with tumors")

# Select 6 sample slices for comparison
sample_slices = []
for f in original_files[:6]:
    slice_num = f.split('_')[1]
    original_path = os.path.join(original_dir, f)
    
    # Find corresponding hybrid file
    hybrid_matches = [h for h in hybrid_files if f"slice_{slice_num}_" in h]
    if hybrid_matches:
        hybrid_path = os.path.join(hybrid_dir, hybrid_matches[0])
        sample_slices.append((slice_num, original_path, hybrid_path))

if not sample_slices:
    print("[ERROR] No matching slices found for comparison")
    sys.exit(1)

print(f"\n[INFO] Creating comparison for {len(sample_slices)} slices...")

# Create comparison figure
fig, axes = plt.subplots(len(sample_slices), 2, figsize=(12, 4*len(sample_slices)))

if len(sample_slices) == 1:
    axes = axes.reshape(1, 2)

for idx, (slice_num, orig_path, hybrid_path) in enumerate(sample_slices):
    # Load images
    orig_img = plt.imread(orig_path)
    hybrid_img = plt.imread(hybrid_path)
    
    # Display original method
    axes[idx, 0].imshow(orig_img)
    axes[idx, 0].set_title(f'Slice {slice_num} - Original U-Net\n(Custom pancreas + tumor)')
    axes[idx, 0].axis('off')
    
    # Display hybrid method
    axes[idx, 1].imshow(hybrid_img)
    axes[idx, 1].set_title(f'Slice {slice_num} - Hybrid\n(TotalSegmentator + Custom tumor)')
    axes[idx, 1].axis('off')

plt.tight_layout()

# Add overall title
fig.suptitle('Method Comparison: Original vs Hybrid', 
             fontsize=16, fontweight='bold', y=1.0)

# Save comparison
output_path = "method_comparison.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"[OK] Comparison saved to: {output_path}")

plt.show()

print("\n" + "="*60)
print("COMPARISON SUMMARY")
print("="*60)
print("\nLEFT COLUMN (Original):")
print("  - Pancreas: Custom U-Net (256x256)")
print("  - Tumor: Custom U-Net (128x128)")
print("  - Training: Your specific dataset")
print("\nRIGHT COLUMN (Hybrid):")
print("  - Pancreas: TotalSegmentator (robust, pre-trained)")
print("  - Tumor: Custom U-Net (same as original)")
print("  - Benefits: Better generalization, clinical-grade pancreas")
print("\nKEY DIFFERENCES:")
print("  - Cyan contours may differ (pancreas segmentation)")
print("  - Red contours should be similar (same tumor model)")
print("  - Hybrid may detect pancreas in more challenging cases")
print("="*60)
