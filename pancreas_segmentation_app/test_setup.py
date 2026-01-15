"""
Test script to verify NIfTI inference server setup
Run this to check if everything is configured correctly
"""
import os
import sys

print("="*60)
print("NIfTI Inference Server - Setup Verification")
print("="*60)
print()

# Check Python packages
print("Checking Python packages...")
packages = {
    'tensorflow': 'TensorFlow',
    'numpy': 'NumPy',
    'cv2': 'OpenCV (opencv-python)',
    'PIL': 'Pillow',
    'nibabel': 'nibabel (for .nii files)',
}

missing_packages = []
for module, name in packages.items():
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name} - NOT INSTALLED")
        missing_packages.append(name)

if missing_packages:
    print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
    print("   Install with: pip install -r requirements_nii.txt")
else:
    print("\n✓ All Python packages installed")

print()

# Check model files
print("Checking model files...")
script_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(os.path.dirname(script_dir), "Model")

models = {
    'unet_best_pancreas.keras': 'Pancreas segmentation model',
    'unet_best_tumor.keras': 'Tumor detection model',
}

missing_models = []
for filename, description in models.items():
    # Check in script dir
    path1 = os.path.join(script_dir, filename)
    path2 = os.path.join(model_dir, filename)
    
    if os.path.exists(path1):
        print(f"  ✓ {description}")
        print(f"    Found at: {path1}")
    elif os.path.exists(path2):
        print(f"  ✓ {description}")
        print(f"    Found at: {path2}")
    else:
        print(f"  ✗ {description} - NOT FOUND")
        print(f"    Searched: {path1}")
        print(f"              {path2}")
        missing_models.append(filename)

if missing_models:
    print(f"\n⚠️  Missing model files: {', '.join(missing_models)}")
    print("   Place models in one of the searched directories")
else:
    print("\n✓ All model files found")

print()
print("="*60)

if missing_packages or missing_models:
    print("❌ Setup incomplete - please resolve the issues above")
    sys.exit(1)
else:
    print("✓ Setup complete! Ready to start the server.")
    print("\nRun: python nii_inference_server.py")
    sys.exit(0)
