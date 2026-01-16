"""
NIfTI CT Scan Inference Server for Two-Stage Pancreas & Tumor Detection
Supports .nii and .nii.gz files
"""
import os
import sys
import json
import base64
import numpy as np
import cv2
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
import tempfile
import gzip

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU only

import tensorflow as tf

# Configure TensorFlow for CPU-only execution
tf.config.set_visible_devices([], 'GPU')

# Optimize CPU performance
tf.config.threading.set_inter_op_parallelism_threads(2)
tf.config.threading.set_intra_op_parallelism_threads(4)

print("[INFO] TensorFlow configured for CPU-only execution")

# Try to import nibabel for .nii file support
try:
    import nibabel as nib
    HAS_NIBABEL = True
    print("[OK] nibabel available")
except ImportError:
    HAS_NIBABEL = False
    print("[WARNING] nibabel not installed. Install with: pip install nibabel")

# Global model references
pancreas_model = None
tumor_model = None
current_volume = None  # Store loaded NIfTI volume for scanning

# Context-aware prediction system
class TumorContext:
    """Maintains context across slices for improved tumor prediction"""
    def __init__(self, context_window=3):
        self.context_window = context_window
        self.history = []  # List of (slice_idx, tumor_mask, tumor_centroid)
        self.reset()
    
    def reset(self):
        """Clear context history"""
        self.history = []
    
    def add_prediction(self, slice_idx, tumor_mask):
        """Add a tumor prediction to history"""
        if tumor_mask is not None and np.any(tumor_mask == 1):
            # Calculate centroid
            ys, xs = np.where(tumor_mask == 1)
            centroid = (np.mean(ys), np.mean(xs))
            self.history.append((slice_idx, tumor_mask.copy(), centroid))
        else:
            self.history.append((slice_idx, None, None))
        
        # Keep only recent history
        if len(self.history) > self.context_window:
            self.history.pop(0)
    
    def get_expected_tumor_region(self):
        """Get expected tumor region based on history"""
        # Find recent slices with tumors
        recent_tumors = [(idx, mask, cent) for idx, mask, cent in self.history 
                        if mask is not None]
        
        if not recent_tumors:
            return None, None
        
        # Get most recent tumor centroid
        _, _, centroid = recent_tumors[-1]
        
        # Average tumor size from recent slices
        avg_area = np.mean([np.sum(mask == 1) for _, mask, _ in recent_tumors])
        
        return centroid, avg_area
    
    def refine_prediction(self, raw_tumor_mask, slice_idx):
        """Refine tumor prediction using context"""
        if raw_tumor_mask is None or not np.any(raw_tumor_mask == 1):
            # Check if we expect tumor based on context
            expected_centroid, expected_area = self.get_expected_tumor_region()
            if expected_centroid and expected_area:
                # We had tumor in recent slices but none detected now
                # Return None to indicate potential miss (could be improved)
                pass
            return raw_tumor_mask
        
        # Apply morphological operations for blob connectivity
        refined = self.enforce_connectivity(raw_tumor_mask)
        
        # Apply temporal smoothing if we have history
        if len(self.history) >= 2:
            refined = self.temporal_smoothing(refined, slice_idx)
        
        return refined
    
    def enforce_connectivity(self, tumor_mask):
        """Ensure tumor appears as connected blobs"""
        # Morphological closing to fill holes and connect nearby regions
        kernel_size = 3
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Close small gaps
        closed = cv2.morphologyEx(tumor_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Remove small isolated regions (noise)
        # Keep only largest connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            closed, connectivity=8
        )
        
        if num_labels <= 1:  # Only background
            return tumor_mask
        
        # Sort components by area (skip background label 0)
        areas = stats[1:, cv2.CC_STAT_AREA]
        if len(areas) == 0:
            return tumor_mask
        
        # Keep components larger than 10 pixels
        min_area = 10
        result = np.zeros_like(tumor_mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                result[labels == i] = 1
        
        return result.astype(np.uint8)
    
    def temporal_smoothing(self, current_mask, slice_idx):
        """Apply temporal smoothing using previous slices"""
        if not self.history:
            return current_mask
        
        # Get previous tumor masks
        prev_masks = [mask for idx, mask, _ in self.history if mask is not None]
        if not prev_masks:
            return current_mask
        
        # Create a weighted average (simple voting)
        # Current slice has higher weight
        vote_map = current_mask.astype(np.float32) * 2.0
        
        # Add votes from previous slices
        for mask in prev_masks[-2:]:  # Last 2 slices
            # Resize if needed
            if mask.shape != current_mask.shape:
                mask_resized = cv2.resize(
                    mask, (current_mask.shape[1], current_mask.shape[0]),
                    interpolation=cv2.INTER_NEAREST
                )
            else:
                mask_resized = mask
            vote_map += mask_resized.astype(np.float32)
        
        # Threshold: require at least 2 votes (current + one previous)
        smoothed = (vote_map >= 2.0).astype(np.uint8)
        
        return smoothed

tumor_context = TumorContext(context_window=3)

# Model paths - check multiple locations
_script_dir = os.path.dirname(os.path.abspath(__file__))
_model_dir = os.path.join(os.path.dirname(_script_dir), "Model")

# Try to find models in multiple locations
PANCREAS_MODEL_PATH = None
TUMOR_MODEL_PATH = None

for search_path in [_script_dir, _model_dir]:
    if PANCREAS_MODEL_PATH is None and os.path.exists(os.path.join(search_path, "unet_best_pancreas.keras")):
        PANCREAS_MODEL_PATH = os.path.join(search_path, "unet_best_pancreas.keras")
    if TUMOR_MODEL_PATH is None and os.path.exists(os.path.join(search_path, "unet_best_tumor.keras")):
        TUMOR_MODEL_PATH = os.path.join(search_path, "unet_best_tumor.keras")

def load_models():
    """Load both pancreas and tumor models"""
    global pancreas_model, tumor_model
    
    if pancreas_model is None:
        print("[INFO] Loading pancreas model...")
        if PANCREAS_MODEL_PATH is None:
            raise FileNotFoundError("unet_best_pancreas.keras not found!")
        pancreas_model = tf.keras.models.load_model(PANCREAS_MODEL_PATH, compile=False)
        print(f"[OK] Pancreas model loaded from: {PANCREAS_MODEL_PATH}")
        print(f"    Input: {pancreas_model.input_shape}")
        print(f"    Output: {pancreas_model.output_shape}")
    
    if tumor_model is None:
        print("[INFO] Loading tumor model...")
        if TUMOR_MODEL_PATH is None:
            raise FileNotFoundError("unet_best_tumor.keras not found!")
        tumor_model = tf.keras.models.load_model(TUMOR_MODEL_PATH, compile=False)
        print(f"[OK] Tumor model loaded from: {TUMOR_MODEL_PATH}")
        print(f"    Input: {tumor_model.input_shape}")
        print(f"    Output: {tumor_model.output_shape}")
    
    return pancreas_model, tumor_model

def hu_window(img):
    """
    HU windowing from the notebook:
    Clip to [-128, 127], then normalize to [0, 1]
    """
    img = np.clip(img, -128, 127)
    img = (img + 128) / 255.0
    return img.astype(np.float32)

def prep_pancreas(img):
    """Prepare image for pancreas model (256x256)"""
    img = hu_window(img)
    img = cv2.resize(img, (256, 256))
    return img[..., None]  # Add channel dimension

def prep_tumor(img):
    """Prepare image for tumor model (128x128)"""
    img = cv2.resize(img, (128, 128))
    return img[..., None]  # Add channel dimension

def load_nii_file(file_bytes):
    """Load .nii or .nii.gz file from bytes"""
    if not HAS_NIBABEL:
        raise ImportError("nibabel not installed. Cannot load .nii files")
    
    # Write bytes to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.nii.gz') as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    try:
        # Load with nibabel
        nii = nib.load(tmp_path)
        vol = nii.get_fdata()
        print(f"[INFO] Loaded NIfTI volume: shape={vol.shape}, dtype={vol.dtype}")
        return vol
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass

def process_ct_slice(slice_data, z_idx, pancreas_model, tumor_model, use_context=True):
    """
    Process a single CT slice through both models with context-aware prediction
    
    Args:
        slice_data: Raw CT slice data
        z_idx: Slice index
        pancreas_model: Pancreas segmentation model
        tumor_model: Tumor detection model
        use_context: Whether to use temporal context for tumor refinement
    
    Returns: dict with results
    """
    global tumor_context
    
    results = {
        'slice_index': z_idx,
        'has_pancreas': False,
        'has_tumor': False,
        'pancreas_mask': None,
        'tumor_mask': None,
        'pancreas_pixels': 0,
        'tumor_pixels': 0,
        'context_refined': False
    }
    
    # Step 1: Pancreas detection
    x_pancreas = prep_pancreas(slice_data)[None, ...]  # Add batch dimension
    pred_pancreas = pancreas_model.predict(x_pancreas, verbose=0)[0]
    mask_pancreas = np.argmax(pred_pancreas, -1).astype(np.uint8)
    
    pancreas_pixels = np.sum(mask_pancreas == 1)
    results['pancreas_pixels'] = int(pancreas_pixels)
    results['pancreas_mask'] = mask_pancreas
    
    if pancreas_pixels > 0:
        results['has_pancreas'] = True
        
        # Step 2: Crop ROI and detect tumor
        ys, xs = np.where(mask_pancreas == 1)
        y1, y2 = ys.min(), ys.max()
        x1, x2 = xs.min(), xs.max()
        
        # Get ROI from normalized image (256x256)
        img_norm = prep_pancreas(slice_data)[..., 0]  # Remove channel
        roi = img_norm[y1:y2, x1:x2]
        
        # Prepare for tumor model
        x_tumor = prep_tumor(roi)[None, ...]
        pred_tumor = tumor_model.predict(x_tumor, verbose=0)[0]
        mask_tumor_128 = np.argmax(pred_tumor, -1).astype(np.uint8)
        
        # Resize tumor mask back to ROI size
        mask_tumor_roi = cv2.resize(
            mask_tumor_128, 
            (x2 - x1, y2 - y1),
            interpolation=cv2.INTER_NEAREST
        )
        
        # Create full-size tumor mask (256x256)
        mask_tumor_full = np.zeros((256, 256), dtype=np.uint8)
        mask_tumor_full[y1:y2, x1:x2] = mask_tumor_roi
        
        # === CONTEXT-AWARE REFINEMENT ===
        if use_context:
            # Refine prediction using temporal context
            mask_tumor_refined = tumor_context.refine_prediction(mask_tumor_full, z_idx)
            
            # Update context with current prediction
            tumor_context.add_prediction(z_idx, mask_tumor_refined)
            
            mask_tumor_full = mask_tumor_refined
            results['context_refined'] = True
        else:
            # Add to context without refinement
            tumor_context.add_prediction(z_idx, mask_tumor_full)
        
        tumor_pixels = np.sum(mask_tumor_full == 1)
        results['tumor_pixels'] = int(tumor_pixels)
        results['tumor_mask'] = mask_tumor_full
        
        if tumor_pixels > 10:  # Threshold to filter noise
            results['has_tumor'] = True
    else:
        # No pancreas detected - update context with None
        if use_context:
            tumor_context.add_prediction(z_idx, None)
    
    return results

def create_overlay(slice_data, pancreas_mask, tumor_mask):
    """Create RGB overlay with pancreas (cyan) and tumor (red)"""
    # Normalize slice to [0, 255]
    img = hu_window(slice_data)
    img = cv2.resize(img, (256, 256))
    img_rgb = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
    
    # Draw pancreas contours (cyan) - thin outline
    if pancreas_mask is not None and np.any(pancreas_mask == 1):
        contours, _ = cv2.findContours(
            pancreas_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(img_rgb, contours, -1, (0, 255, 255), 1)  # Cyan (RGB)
    
    # Draw tumor contours (red) - thin outline
    if tumor_mask is not None and np.any(tumor_mask == 1):
        contours, _ = cv2.findContours(
            tumor_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(img_rgb, contours, -1, (255, 0, 0), 1)  # Red (RGB)
    
    return img_rgb

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Health check endpoint"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'ok',
                'models_loaded': pancreas_model is not None and tumor_model is not None,
                'nibabel_available': HAS_NIBABEL
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle inference requests"""
        if self.path == '/load_nii':
            self._handle_load_nii()
        elif self.path == '/scan_slice':
            self._handle_scan_slice()
        elif self.path == '/scan_all':
            self._handle_scan_all()
        elif self.path == '/reset_context':
            self._handle_reset_context()
        else:
            self.send_error(404)
    
    def _handle_load_nii(self):
        """Load .nii file and extract all slices"""
        global current_volume, tumor_context
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Decode base64 file
            file_bytes = base64.b64decode(data['file'])
            
            # Load NIfTI file
            volume = load_nii_file(file_bytes)
            
            # Store volume globally for scan_slice endpoint
            current_volume = volume
            
            # Reset tumor context for new volume
            tumor_context.reset()
            print(f"[INFO] Context reset for new volume")
            
            # Extract all slices as base64-encoded PNGs
            slices = []
            for z in range(volume.shape[2]):
                slice_data = volume[:, :, z]
                
                # Convert to image for preview
                img = hu_window(slice_data)
                img_uint8 = (img * 255).astype(np.uint8)
                
                # Encode as PNG
                img_pil = Image.fromarray(img_uint8, mode='L')
                buffer = BytesIO()
                img_pil.save(buffer, format='PNG')
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                
                slices.append({
                    'index': z,
                    'image': img_b64,
                    'shape': list(slice_data.shape)
                })
            
            response = {
                'success': True,
                'num_slices': len(slices),
                'volume_shape': list(volume.shape),
                'slices': slices
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def _handle_scan_slice(self):
        """Scan a single slice with both models"""
        global current_volume
        try:
            # Load models if not loaded
            p_model, t_model = load_models()
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            z_idx = data['slice_index']
            
            # Check if volume is loaded
            if current_volume is None:
                raise ValueError("No volume loaded. Please load a NIfTI file first.")
            
            # Get slice from stored volume
            slice_data = current_volume[:, :, z_idx]
            
            # Process through both models
            results = process_ct_slice(slice_data, z_idx, p_model, t_model)
            
            # Create overlay
            overlay_img = create_overlay(
                slice_data,
                results['pancreas_mask'],
                results['tumor_mask']
            )
            
            # Encode overlay as PNG
            overlay_pil = Image.fromarray(overlay_img, mode='RGB')
            buffer = BytesIO()
            overlay_pil.save(buffer, format='PNG')
            overlay_b64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Prepare response
            response = {
                'success': True,
                'slice_index': z_idx,
                'has_pancreas': results['has_pancreas'],
                'has_tumor': results['has_tumor'],
                'pancreas_pixels': results['pancreas_pixels'],
                'tumor_pixels': results['tumor_pixels'],
                'overlay': overlay_b64
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def _handle_scan_all(self):
        """Scan all slices sequentially with context awareness"""
        global current_volume, tumor_context
        try:
            # Load models if not loaded
            p_model, t_model = load_models()
            
            # Check if volume is loaded
            if current_volume is None:
                raise ValueError("No volume loaded. Please load a NIfTI file first.")
            
            # Reset context for clean sequential processing
            tumor_context.reset()
            
            # Process all slices
            num_slices = current_volume.shape[2]
            results_list = []
            
            print(f"[INFO] Scanning all {num_slices} slices with context awareness...")
            
            for z_idx in range(num_slices):
                slice_data = current_volume[:, :, z_idx]
                
                # Process with context
                results = process_ct_slice(slice_data, z_idx, p_model, t_model, use_context=True)
                
                # Create overlay
                overlay_img = create_overlay(
                    slice_data,
                    results['pancreas_mask'],
                    results['tumor_mask']
                )
                
                # Encode overlay as PNG
                overlay_pil = Image.fromarray(overlay_img, mode='RGB')
                buffer = BytesIO()
                overlay_pil.save(buffer, format='PNG')
                overlay_b64 = base64.b64encode(buffer.getvalue()).decode()
                
                # Add to results
                results_list.append({
                    'slice_index': z_idx,
                    'has_pancreas': results['has_pancreas'],
                    'has_tumor': results['has_tumor'],
                    'pancreas_pixels': results['pancreas_pixels'],
                    'tumor_pixels': results['tumor_pixels'],
                    'context_refined': results.get('context_refined', False),
                    'overlay': overlay_b64
                })
                
                # Progress update
                if (z_idx + 1) % 10 == 0:
                    print(f"[INFO] Processed {z_idx + 1}/{num_slices} slices")
            
            # Prepare response
            response = {
                'success': True,
                'num_slices': num_slices,
                'results': results_list,
                'summary': {
                    'slices_with_pancreas': sum(1 for r in results_list if r['has_pancreas']),
                    'slices_with_tumor': sum(1 for r in results_list if r['has_tumor']),
                    'total_slices': num_slices
                }
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
            print(f"[OK] Scan complete! Pancreas: {response['summary']['slices_with_pancreas']}, Tumor: {response['summary']['slices_with_tumor']}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def _handle_reset_context(self):
        """Reset the tumor context (useful when scanning non-sequentially)"""
        global tumor_context
        try:
            tumor_context.reset()
            
            response = {
                'success': True,
                'message': 'Context reset successfully'
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
            print("[INFO] Tumor context reset")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())

def main():
    """Start the server"""
    PORT = 8765
    
    print("\n" + "="*60)
    print("NIfTI CT Scan Inference Server")
    print("Two-Stage Pancreas & Tumor Detection")
    print("="*60)
    
    # Check models
    if PANCREAS_MODEL_PATH:
        print(f"[OK] Pancreas model: {PANCREAS_MODEL_PATH}")
    else:
        print("[ERROR] Pancreas model not found!")
    
    if TUMOR_MODEL_PATH:
        print(f"[OK] Tumor model: {TUMOR_MODEL_PATH}")
    else:
        print("[ERROR] Tumor model not found!")
    
    if not HAS_NIBABEL:
        print("[WARNING] nibabel not installed - .nii files not supported")
        print("          Install with: pip install nibabel")
    
    # Pre-load models on startup
    print("\n[INFO] Pre-loading models...")
    try:
        load_models()
        print("[OK] Models pre-loaded successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")
    
    print(f"\nStarting server on port {PORT}...")
    print(f"Endpoints:")
    print(f"  GET  /health          - Health check")
    print(f"  POST /load_nii        - Load .nii/.nii.gz file")
    print(f"  POST /scan_slice      - Scan single slice (with context)")
    print(f"  POST /scan_all        - Scan all slices (batch, context-aware)")
    print(f"  POST /reset_context   - Reset tumor context")
    print(f"\nFeatures:")
    print(f"  [NEW] Context-aware tumor prediction")
    print(f"  [NEW] Temporal smoothing across slices")
    print(f"  [NEW] Blob connectivity enforcement")
    print("="*60 + "\n")
    
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"[OK] Server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()
