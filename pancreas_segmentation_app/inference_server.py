"""
Local inference server for Windows desktop
Runs the Keras model directly for segmentation
"""
import os
import sys
import json
import base64
import numpy as np
import cv2
import tempfile
import nibabel as nib
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
import warnings

# Suppress annoying warnings from TensorFlow/Keras
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# import tensorflow as tf # Lazy load for speed

# Global model reference
model = None
interpreter = None
# Auto-detect model path - check local folder first
_script_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_script_dir, "unet_best.keras")
TFLITE_MODEL_PATH = os.path.join(_script_dir, "assets", "models", "unet_model.tflite")

def load_model():
    """Load the model (prefer TFLite for speed, fallback to Keras)"""
    global model, interpreter
    
    if interpreter is None and model is None:
        print("[INFO] Loading model...")
        
        # Try TFLite first (Much faster load time)
        if os.path.exists(TFLITE_MODEL_PATH):
            try:
                print(f"[INFO] Found TFLite model at {TFLITE_MODEL_PATH}")
                # 1. Try ai_edge_litert (Next Gen TFLite)
                try:
                    from ai_edge_litert.interpreter import Interpreter
                    interpreter = Interpreter(model_path=TFLITE_MODEL_PATH)
                    print("[INFO] Using ai_edge_litert runtime")
                except ImportError:
                    # 2. Try tflite_runtime (Legacy lightweight)
                    try:
                        import tflite_runtime.interpreter as tflite
                        interpreter = tflite.Interpreter(model_path=TFLITE_MODEL_PATH)
                        print("[INFO] Using tflite_runtime")
                    except ImportError:
                        # 3. Fallback to full TensorFlow
                        print("[INFO] Specialized runtimes not installed. Falling back to standard TensorFlow (startup may be slower)...")
                        # This import is heavy, which is why we only do it if necessary
                        import tensorflow as tf
                        interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
                
                interpreter.allocate_tensors()
                
                input_details = interpreter.get_input_details()
                output_details = interpreter.get_output_details()
                
                print(f"[OK] TFLite Model loaded!")
                print(f"    Input: {input_details[0]['shape']}")
                print(f"    Output: {output_details[0]['shape']}")
                return interpreter
            except Exception as e:
                print(f"[WARNING] Failed to load TFLite model: {e}")
                print("[INFO] Falling back to Keras model...")
                interpreter = None

        # Fallback to Keras
        if os.path.exists(MODEL_PATH):
            import tensorflow as tf
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            print("[OK] Keras Model loaded!")
            print(f"    Input: {model.input_shape}")
            print(f"    Output: {model.output_shape}")
            return model
        else:
            print("[ERROR] No model found!")
    
    return interpreter if interpreter else model

def hu_window(img):
    """
    HU windowing according to paper (same as Gradio app):
    HU <= -128  -> 0
    HU >= 127   -> 255
    Normalize to [0, 1]
    """
    img = np.clip(img, -128, 127)
    img = (img + 128) / 255.0
    return img.astype(np.float32)

def is_processed_image(image):
    """
    Detect if image is already processed - EXACTLY matching Gradio's logic
    Uses scoring system based on value range, shape, and dtype
    """
    reasons = []
    score = 0
    
    min_val, max_val = image.min(), image.max()
    
    print(f"[DEBUG] Image stats: min={min_val:.2f}, max={max_val:.2f}, shape={image.shape}, dtype={image.dtype}")
    
    # If values are in typical HU range (-1024 to 3071), definitely unprocessed
    if min_val < -100 or max_val > 300:
        print(f"[DEBUG] -> RAW HU CT detected")
        return False
    
    # If values are in [0, 1] range, likely already processed
    if 0 <= min_val and max_val <= 1.0:
        score += 2
        reasons.append("Values in [0,1] range")
    # If values are in [0, 255] range (uint8 normalized), might be processed PNG
    elif 0 <= min_val and max_val <= 255:
        score += 1
        reasons.append("Values in [0,255] range")
    
    # Check shape - processed images are typically square 256x256 or 128x128
    if len(image.shape) >= 2 and image.shape[0] == image.shape[1] and image.shape[0] in [128, 256, 512]:
        score += 1
        reasons.append(f"Square shape {image.shape[0]}x{image.shape[1]}")
    
    # Check dtype
    if image.dtype in [np.float32, np.float64]:
        score += 1
        reasons.append("Float dtype")
    
    is_processed = score >= 2
    status = "PROCESSED" if is_processed else "UNPROCESSED"
    print(f"[DEBUG] -> {status} (score={score}): {', '.join(reasons)}")
    
    return is_processed

def preprocess_image(image_data):
    """Preprocess image for inference - EXACTLY matching Gradio app"""
    import cv2
    
    # Decode base64 image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    
    # Convert to numpy array - use uint8 first like Gradio does
    img_array = np.array(image)
    
    print(f"[PREPROCESS] Original image: shape={img_array.shape}, dtype={img_array.dtype}")
    
    # Convert to grayscale if needed (matches Gradio's behavior)
    if len(img_array.shape) == 3:
        if img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
        else:  # RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        print(f"[PREPROCESS] Converted to grayscale: shape={img_array.shape}")
    
    # Convert to float32 for processing
    img_array = img_array.astype(np.float32)
    
    # Detect if already processed using Gradio's scoring system
    is_processed = is_processed_image(img_array)
    
    if not is_processed:
        # Apply HU windowing for raw CT
        img_array = hu_window(img_array)
        print(f"[PREPROCESS] Applied HU windowing")
    else:
        # Already processed, just ensure float32 and [0,1] range
        if img_array.max() > 1.0:
            img_array = img_array / 255.0
        print(f"[PREPROCESS] Image already processed, normalized to [0,1]")
    
    print(f"[PREPROCESS] Final: min={img_array.min():.4f}, max={img_array.max():.4f}")
    

    # Resize to model input size (128x128)
    # img_array = cv2.resize(img_array, (128, 128))
    
    # Save debug image to compare with Gradio
    debug_img = (img_array * 255).astype(np.uint8)
    cv2.imwrite("debug_preprocessed.png", debug_img)
    print(f"[DEBUG] Saved preprocessed image to debug_preprocessed.png")
    
    # Add batch and channel dimensions: (1, 128, 128, 1) if we were resizing here
    # But now we return the full 2D array (normalized) to let the pipeline handle cropping
    # img_array = img_array.reshape(1, 128, 128, 1)
    
    return img_array

def postprocess_output(output, original_image_b64=None, crop_info=None):
    """
    Convert model output to segmentation mask
    crop_info: dict with 'y_start', 'y_end', 'x_start', 'x_end', 'orig_shape' if cropping was used
    """
    # output shape: (1, 128, 128, 2)
    # Take argmax to get class predictions
    mask = np.argmax(output[0], axis=-1)  # (128, 128)
    
    # Debug: print tumor statistics
    tumor_pixels = np.sum(mask == 1)
    print(f"[POSTPROCESS] Tumor pixels detected: {tumor_pixels} ({tumor_pixels/128/128*100:.2f}%)")
    
    # UN-CROP LOGIC: If we cropped the input, we must place the mask back into the full frame
    if crop_info:
        # 1. Resize the 128x128 mask back to the CROP size
        crop_h = crop_info['y_end'] - crop_info['y_start']
        crop_w = crop_info['x_end'] - crop_info['x_start']
        
        # Use Nearest Neighbor for mask resizing to keep 0/1 values
        mask_crop = cv2.resize(mask.astype(np.uint8), (crop_w, crop_h), interpolation=cv2.INTER_NEAREST)
        
        # 2. Create a blank mask of the original full image size
        full_mask = np.zeros(crop_info['orig_shape'], dtype=np.uint8)
        
        # 3. Place the resized crop mask into the center
        full_mask[crop_info['y_start']:crop_info['y_end'], crop_info['x_start']:crop_info['x_end']] = mask_crop
        
        # Update mask reference to the full size one
        mask = full_mask
        print(f"[POSTPROCESS] Un-cropped mask to size {mask.shape}")
        
    # Convert to uint8 (0 or 255) for PNG
    mask_img = (mask * 255).astype(np.uint8)
    
    # Save debug mask
    cv2.imwrite("debug_mask.png", mask_img)
    print(f"[DEBUG] Saved mask to debug_mask.png")
    
    # PNG version of mask
    mask_image = Image.fromarray(mask_img, mode='L')
    buffer = BytesIO()
    mask_image.save(buffer, format='PNG')
    mask_png_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Raw mask as base64 bytes (0 or 1 values)
    mask_flat = mask.flatten().astype(np.uint8)
    mask_raw_b64 = base64.b64encode(mask_flat.tobytes()).decode('utf-8')
    
    # Generate overlay image on server side
    overlay_b64 = None
    if original_image_b64:
        try:
            # Decode original image
            img_bytes = base64.b64decode(original_image_b64)
            img_pil = Image.open(BytesIO(img_bytes))
            img_array = np.array(img_pil)
            
            # Resize mask to match original image size
            mask_resized = cv2.resize(mask_img, (img_array.shape[1], img_array.shape[0]), interpolation=cv2.INTER_NEAREST)
            
            # Convert grayscale to RGB if needed
            if len(img_array.shape) == 2:
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            else:
                img_rgb = img_array.copy()
            
            # Create overlay: red tint where mask is white (tumor)
            overlay = img_rgb.copy()
            tumor_mask = mask_resized > 127
            
            # Blend with red for tumor regions (50% original + 50% red)
            overlay[tumor_mask, 0] = np.clip(overlay[tumor_mask, 0] * 0.5 + 127, 0, 255).astype(np.uint8)  # R
            overlay[tumor_mask, 1] = (overlay[tumor_mask, 1] * 0.5).astype(np.uint8)  # G
            overlay[tumor_mask, 2] = (overlay[tumor_mask, 2] * 0.5).astype(np.uint8)  # B
            
            # Save debug overlay
            cv2.imwrite("debug_overlay.png", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            print(f"[DEBUG] Saved overlay to debug_overlay.png")
            
            # Encode to base64
            overlay_pil = Image.fromarray(overlay)
            buffer = BytesIO()
            overlay_pil.save(buffer, format='PNG')
            overlay_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"[ERROR] Failed to generate overlay: {e}")
    
    return mask_png_b64, mask_raw_b64, int(tumor_pixels), overlay_b64

def process_nii_file(file_content_b64):
    """
    Process uploaded .nii.gz file content (base64 string)
    Returns a list of base64 encoded PNG images of the slices
    """
    import tempfile
    
    slices_data = []
    temp_path = None
    
    try:
        # Decode base64 to bytes
        file_bytes = base64.b64decode(file_content_b64)
        
        # Save bytes to temp file because nibabel needs a file path usually
        # We need a suffix so nibabel knows format
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        print(f"[NII] Saved temp file at {temp_path}")
        
        # Load with nibabel
        img_nii = nib.load(temp_path).get_fdata()
        
        # It is usually (H, W, D) -> (Height, Width, Depth/Slices)
        # Iterate over Z axis (Depth)
        if len(img_nii.shape) != 3:
             print(f"[ERROR] NIfTI file has shape {img_nii.shape}, expected 3D.")
             return []

        depth = img_nii.shape[2]
        
        print(f"[NII] Loaded NIfTI file. Shape: {img_nii.shape}")
        
        for z in range(depth):
            img_slice = img_nii[:, :, z]
            
            # Apply HU windowing
            img_slice = hu_window(img_slice)
            
            # Resize to TARGET_SIZE (256x256) for display/segmentation
            img_resized = cv2.resize(img_slice, (256, 256))
            
            # Convert to uint8 [0, 255] for PNG
            img_uint8 = (img_resized * 255).astype(np.uint8)
            
            # Convert to PNG Base64
            image_pil = Image.fromarray(img_uint8, mode='L')
            buffer = BytesIO()
            image_pil.save(buffer, format='PNG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            slices_data.append({
                "index": z,
                "image": img_b64
            })
            
    except Exception as e:
        print(f"[ERROR] processing nii file: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
            
    return slices_data

class SegmentationHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        """Send CORS headers for web browser access"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        if self.path == '/upload_nii':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                # Get file data
                file_b64 = data.get('file_data')
                if not file_b64:
                    self.send_error(400, 'Missing file_data')
                    return
                
                print(f"[INFO] Received .nii.gz file upload")
                
                # Process
                slices = process_nii_file(file_b64)
                
                response_data = {
                    'success': True,
                    'slices_count': len(slices),
                    'slices': slices
                }
                
                # Use default=str to handle any non-serializable types if any, strict=False helps with NaN etc.
                response = json.dumps(response_data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(response.encode())
                
            except Exception as e:
                print(f"[ERROR] Upload handler: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': str(e)
                })
                self.wfile.write(error_response.encode())
                
        elif self.path == '/segment':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body)
                
                # Get image data
                image_b64 = data.get('image')
                if not image_b64:
                    self.send_error(400, 'Missing image data')
                    return
                
                # Preprocess - returns normalized image array (H, W) or (H, W, 1)
                full_img_array = preprocess_image(image_b64)
                
                # Squeeze channel dim if present for shape checking
                if len(full_img_array.shape) == 3:
                     check_img = full_img_array[:, :, 0]
                else:
                     check_img = full_img_array
                     
                h, w = check_img.shape
                crop_info = None
                input_tensor = None
                
                # SMART CROP LOGIC:
                # If image is significantly larger than model input, crop center
                # This fixes the "Huge Overlay" issue when feeding full slices to cropped-trained model
                if h >= 200 and w >= 200:
                    # Crop Center 160x160 (Approx covering pancreas)
                    crop_size = 160
                    cy, cx = h // 2, w // 2
                    
                    y_start = max(0, cy - crop_size // 2)
                    x_start = max(0, cx - crop_size // 2)
                    y_end = min(h, y_start + crop_size)
                    x_end = min(w, x_start + crop_size)
                    
                    crop_img = full_img_array[y_start:y_end, x_start:x_end]
                    
                    # Resize to model input 128x128
                    input_resize = cv2.resize(crop_img, (128, 128))
                    input_tensor = input_resize.reshape(1, 128, 128, 1)
                    
                    crop_info = {
                        'y_start': y_start, 'y_end': y_end,
                        'x_start': x_start, 'x_end': x_end,
                        'orig_shape': (h, w)
                    }
                    print(f"[CROP] Applied Center Crop: {x_start}:{x_end}, {y_start}:{y_end} from {w}x{h}")
                else:
                    # Small enough, assume it's already a crop
                    print(f"[NO-CROP] Image size {w}x{h} <= 200, processing full image")
                    input_resize = cv2.resize(full_img_array, (128, 128))
                    input_tensor = input_resize.reshape(1, 128, 128, 1)
                
                # Run inference
                load_model() # Ensure model is loaded
                
                output = None
                if interpreter is not None:
                     # TFLite Inference
                     input_details = interpreter.get_input_details()
                     output_details = interpreter.get_output_details()
                     
                     # Check if resize needed for input tensor (TFLite fixed size)
                     # input_tensor is already resized to 128x128 in previous steps
                     
                     interpreter.set_tensor(input_details[0]['index'], input_tensor)
                     interpreter.invoke()
                     output = interpreter.get_tensor(output_details[0]['index'])
                else:
                     # Keras Inference
                     output = model.predict(input_tensor, verbose=0)
                
                # Postprocess - pass original image to generate overlay
                # Pass crop_info so postprocess can restore mask to full size
                mask_png_b64, mask_raw_b64, tumor_pixels, overlay_b64 = postprocess_output(output, image_b64, crop_info)
                
                # Send response with overlay image
                # mask_width/height should reflect the logical usage, but we returned full size mask strings
                # so the frontend should map them to originalWidth/Height
                response_data = {
                    'success': True,
                    'mask': mask_png_b64,
                    'mask_raw': mask_raw_b64,
                    'tumor_pixels': tumor_pixels,
                    'mask_width': 128, # Legacy field, raw mask is actually full size now if uncropped
                    'mask_height': 128
                }
                
                # Add overlay if generated successfully
                if overlay_b64:
                    response_data['overlay'] = overlay_b64
                
                response = json.dumps(response_data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(response.encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': str(e)
                })
                self.wfile.write(error_response.encode())
        
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        print(f"[SERVER] {args[0]}")

def main():
    port = 8765
    host = '0.0.0.0'  # Listen on all interfaces for network access

    # Pre-load model (Optional - Commented out to make server start instantly)
    # The model will load automatically upon the first request.
    # load_model()

    # Get local IP for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "your-ip"

    # Start server
    server = HTTPServer((host, port), SegmentationHandler)
    print(f"\n[INFO] Inference server running at:")
    print(f"       - Local:   http://localhost:{port}")
    print(f"       - Network: http://{local_ip}:{port}")
    print("[INFO] Endpoints:")
    print(f"       POST /segment - Run segmentation")
    print(f"       GET  /health  - Health check")
    print(f"\n[INFO] For Android/Web app, use: http://{local_ip}:{port}")
    print(f"[INFO] CORS enabled for web browser access")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down server...")
        server.shutdown()

if __name__ == '__main__':
    main()
