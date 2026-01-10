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
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf

# Global model reference
model = None
# Auto-detect model path - check local folder first, then Gradio Web App folder
_script_dir = os.path.dirname(os.path.abspath(__file__))
_gradio_model = os.path.join(os.path.dirname(_script_dir), "Gradio Web App", "unet_best.keras")
MODEL_PATH = _gradio_model if os.path.exists(_gradio_model) else r"I:\My Drive\Colab Notebooks\Gradio Web App\unet_best.keras"

def load_model():
    """Load the Keras model"""
    global model
    if model is None:
        print("[INFO] Loading model...")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        print("[OK] Model loaded!")
        print(f"    Input: {model.input_shape}")
        print(f"    Output: {model.output_shape}")
    return model

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
    img_array = cv2.resize(img_array, (128, 128))
    
    # Save debug image to compare with Gradio
    debug_img = (img_array * 255).astype(np.uint8)
    cv2.imwrite("debug_preprocessed.png", debug_img)
    print(f"[DEBUG] Saved preprocessed image to debug_preprocessed.png")
    
    # Add batch and channel dimensions: (1, 128, 128, 1)
    img_array = img_array.reshape(1, 128, 128, 1)
    
    return img_array

def postprocess_output(output, original_image_b64=None):
    """Convert model output to segmentation mask"""
    # output shape: (1, 128, 128, 2)
    # Take argmax to get class predictions
    mask = np.argmax(output[0], axis=-1)  # (128, 128)
    
    # Debug: print tumor statistics
    tumor_pixels = np.sum(mask == 1)
    print(f"[POSTPROCESS] Tumor pixels detected: {tumor_pixels} ({tumor_pixels/128/128*100:.2f}%)")
    
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
        if self.path == '/segment':
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
                
                # Preprocess
                input_data = preprocess_image(image_b64)
                
                # Run inference
                model = load_model()
                output = model.predict(input_data, verbose=0)
                
                # Postprocess - pass original image to generate overlay
                mask_png_b64, mask_raw_b64, tumor_pixels, overlay_b64 = postprocess_output(output, image_b64)
                
                # Send response with overlay image
                response_data = {
                    'success': True,
                    'mask': mask_png_b64,
                    'mask_raw': mask_raw_b64,
                    'tumor_pixels': tumor_pixels,
                    'mask_width': 128,
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

    # Pre-load model
    load_model()

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
