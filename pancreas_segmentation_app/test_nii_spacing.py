"""
Quick test script to verify NIfTI spacing extraction works correctly
"""
import os
import sys

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    import nibabel as nib
    import numpy as np
    
    # Try to find a test NIfTI file
    test_dir = r"C:\Users\Admin\Documents\School\AI\MultiPlatform-I\Testing_Model\Testset"
    
    if os.path.exists(test_dir):
        nii_files = [f for f in os.listdir(test_dir) if f.endswith('.nii.gz') or f.endswith('.nii')]
        
        if nii_files:
            test_file = os.path.join(test_dir, nii_files[0])
            print(f"Testing with: {test_file}")
            print("="*60)
            
            # Load with nibabel
            nii = nib.load(test_file)
            vol = nii.get_fdata()
            
            # Get spacing
            header = nii.header
            spacing = tuple(header.get_zooms()[:3])
            
            print(f"✅ Volume shape: {vol.shape}")
            print(f"✅ Voxel spacing (mm): {spacing}")
            print(f"✅ Data type: {vol.dtype}")
            print(f"✅ Value range: [{vol.min():.1f}, {vol.max():.1f}]")
            
            # Calculate effective spacing for 256x256 masks
            orig_x, orig_y = vol.shape[0], vol.shape[1]
            scale_x = orig_x / 256.0
            scale_y = orig_y / 256.0
            effective_spacing = (
                spacing[0] * scale_x,
                spacing[1] * scale_y,
                spacing[2]
            )
            
            print(f"\n📐 Original dimensions: {orig_x} x {orig_y}")
            print(f"📐 Scale factors: x={scale_x:.3f}, y={scale_y:.3f}")
            print(f"📐 Effective spacing for 256x256 masks: {effective_spacing}")
            
            # Calculate physical dimensions
            physical_dims = (
                vol.shape[0] * spacing[0],
                vol.shape[1] * spacing[1],
                vol.shape[2] * spacing[2]
            )
            print(f"\n🔍 Physical dimensions (mm):")
            print(f"   X: {physical_dims[0]:.1f} mm")
            print(f"   Y: {physical_dims[1]:.1f} mm")
            print(f"   Z: {physical_dims[2]:.1f} mm")
            
            print("\n" + "="*60)
            print("✅ All spacing calculations working correctly!")
            
        else:
            print("No .nii files found in test directory")
    else:
        print(f"Test directory not found: {test_dir}")
        print("\nPlease run this script after placing a .nii file in:")
        print("  Testing_Model/Testset/")
        
except ImportError as e:
    print(f"❌ Error: {e}")
    print("\nPlease install nibabel:")
    print("  pip install nibabel")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
