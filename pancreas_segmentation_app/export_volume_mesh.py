"""
Quick script to export CT volume as mesh for Windows 3D Viewer testing
"""
import requests
import json

# Server URL
SERVER = "http://localhost:8765"

def export_volume_mesh(threshold=200, downsample=2):
    """
    Export the currently loaded CT volume as a mesh
    
    Args:
        threshold: HU threshold for marching cubes (200 = bone)
        downsample: Downsample factor (2 = half resolution, faster)
    """
    print(f"Exporting volume mesh with threshold={threshold}, downsample={downsample}...")
    
    response = requests.post(
        f"{SERVER}/export_volume_mesh",
        json={
            'threshold': threshold,
            'downsample': downsample
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("\n✅ SUCCESS!")
            print(f"📁 File saved to: {result['file_path']}")
            print(f"📊 Mesh stats:")
            print(f"   - Vertices: {result['vertices']:,}")
            print(f"   - Faces: {result['faces']:,}")
            print(f"   - File size: {result['size_bytes']:,} bytes ({result['size_bytes']/1024/1024:.2f} MB)")
            print(f"\n💡 To view:")
            print(f"   1. Open File Explorer")
            print(f"   2. Navigate to: pancreas_segmentation_app folder")
            print(f"   3. Double-click 'ct_volume_export.glb'")
            print(f"   4. Windows 3D Viewer will open automatically")
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Server error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("="*60)
    print("CT Volume Mesh Export Tool")
    print("="*60)
    print("\nMake sure:")
    print("  1. Server is running (python nii_inference_server.py)")
    print("  2. A NIfTI file has been loaded")
    print()
    
    # Try to check server health
    try:
        health = requests.get(f"{SERVER}/health", timeout=2)
        if health.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding correctly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print(f"   Make sure server is running on {SERVER}")
        exit(1)
    
    print("\nExporting with bone threshold (200 HU)...")
    success = export_volume_mesh(threshold=200, downsample=2)
    
    if success:
        print("\n" + "="*60)
        print("You can also try different thresholds:")
        print("  - Soft tissue: 50 HU")
        print("  - Muscle: 100 HU")
        print("  - Bone: 200 HU")
        print("  - Dense bone: 400 HU")
        print("\nExample:")
        print("  python export_volume_mesh.py")
        print("  # Then modify threshold in the script")
        print("="*60)
