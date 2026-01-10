"""
Direct comparison test between Gradio and Flutter server preprocessing
"""
import os
import sys
import numpy as np
import cv2
from PIL import Image

# Add Gradio app path
sys.path.insert(0, r"I:\My Drive\Colab Notebooks\Gradio Web App")

# Test image path
TEST_IMAGE = r"I:\My Drive\Colab Notebooks\NPY_PNG_Converter_App\png_output\image_only\pancreas_278\pancreas_278_slice051.png"

def load_gradio_model():
    """Load the same model Gradio uses"""
    import tensorflow as tf
    MODEL_PATH = r"I:\My Drive\Colab Notebooks\Gradio Web App\unet_best.keras"
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    return model

def gradio_preprocess(image_path):
    """Preprocess exactly like Gradio does"""
    # Load image as numpy (like Gradio's type="numpy")
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Gradio loads as RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    print(f"[GRADIO] Loaded image: shape={img.shape}, dtype={img.dtype}")
    
    # Convert to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    print(f"[GRADIO] Grayscale: shape={img.shape}, dtype={img.dtype}")
    
    # Check if processed (Gradio's scoring system)
    min_val, max_val = img.min(), img.max()
    score = 0
    
    if 0 <= min_val and max_val <= 1.0:
        score += 2
    elif 0 <= min_val and max_val <= 255:
        score += 1
    
    if img.shape[0] == img.shape[1] and img.shape[0] in [128, 256, 512]:
        score += 1
    
    if img.dtype in [np.float32, np.float64]:
        score += 1
    
    is_processed = score >= 2
    print(f"[GRADIO] Detection: min={min_val}, max={max_val}, score={score}, is_processed={is_processed}")
    
    # Convert to float
    img = img.astype(np.float32)
    
    if not is_processed:
        # Apply HU windowing
        img = np.clip(img, -128, 127)
        img = (img + 128) / 255.0
        print(f"[GRADIO] Applied HU windowing")
    else:
        # Already processed
        if img.max() > 1.0:
            img = img / 255.0
        print(f"[GRADIO] Normalized to [0,1]")
    
    print(f"[GRADIO] Final: min={img.min():.4f}, max={img.max():.4f}")
    
    # Resize
    img = cv2.resize(img, (128, 128))
    
    # Save for comparison
    cv2.imwrite("gradio_preprocessed.png", (img * 255).astype(np.uint8))
    
    return img.reshape(1, 128, 128, 1)

def flutter_preprocess(image_path):
    """Preprocess exactly like Flutter server does"""
    # Load with PIL (like server does from base64)
    image = Image.open(image_path)
    img = np.array(image)
    
    print(f"[FLUTTER] Loaded image: shape={img.shape}, dtype={img.dtype}")
    
    # Convert to grayscale
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        print(f"[FLUTTER] Grayscale: shape={img.shape}")
    
    # Convert to float
    img = img.astype(np.float32)
    
    # Check if processed (same scoring)
    min_val, max_val = img.min(), img.max()
    score = 0
    
    if 0 <= min_val and max_val <= 1.0:
        score += 2
    elif 0 <= min_val and max_val <= 255:
        score += 1
    
    if len(img.shape) >= 2 and img.shape[0] == img.shape[1] and img.shape[0] in [128, 256, 512]:
        score += 1
    
    if img.dtype in [np.float32, np.float64]:
        score += 1
    
    is_processed = score >= 2
    print(f"[FLUTTER] Detection: min={min_val}, max={max_val}, score={score}, is_processed={is_processed}")
    
    if not is_processed:
        # Apply HU windowing
        img = np.clip(img, -128, 127)
        img = (img + 128) / 255.0
        print(f"[FLUTTER] Applied HU windowing")
    else:
        if img.max() > 1.0:
            img = img / 255.0
        print(f"[FLUTTER] Normalized to [0,1]")
    
    print(f"[FLUTTER] Final: min={img.min():.4f}, max={img.max():.4f}")
    
    # Resize
    img = cv2.resize(img, (128, 128))
    
    # Save for comparison
    cv2.imwrite("flutter_preprocessed.png", (img * 255).astype(np.uint8))
    
    return img.reshape(1, 128, 128, 1)

def main():
    if not os.path.exists(TEST_IMAGE):
        print(f"ERROR: Test image not found: {TEST_IMAGE}")
        print("Please update TEST_IMAGE path in this script")
        return
    
    print("="*60)
    print("Loading model...")
    model = load_gradio_model()
    print(f"Model loaded: input={model.input_shape}, output={model.output_shape}")
    
    print("\n" + "="*60)
    print("GRADIO PREPROCESSING:")
    print("="*60)
    gradio_input = gradio_preprocess(TEST_IMAGE)
    
    print("\n" + "="*60)
    print("FLUTTER PREPROCESSING:")
    print("="*60)
    flutter_input = flutter_preprocess(TEST_IMAGE)
    
    print("\n" + "="*60)
    print("COMPARISON:")
    print("="*60)
    diff = np.abs(gradio_input - flutter_input)
    print(f"Max difference: {diff.max():.6f}")
    print(f"Mean difference: {diff.mean():.6f}")
    print(f"Are they identical: {np.allclose(gradio_input, flutter_input)}")
    
    print("\n" + "="*60)
    print("RUNNING INFERENCE:")
    print("="*60)
    
    gradio_output = model.predict(gradio_input, verbose=0)
    flutter_output = model.predict(flutter_input, verbose=0)
    
    gradio_mask = np.argmax(gradio_output[0], axis=-1)
    flutter_mask = np.argmax(flutter_output[0], axis=-1)
    
    gradio_tumor = np.sum(gradio_mask == 1)
    flutter_tumor = np.sum(flutter_mask == 1)
    
    print(f"Gradio tumor pixels: {gradio_tumor} ({gradio_tumor/128/128*100:.2f}%)")
    print(f"Flutter tumor pixels: {flutter_tumor} ({flutter_tumor/128/128*100:.2f}%)")
    
    # Save masks
    cv2.imwrite("gradio_mask.png", (gradio_mask * 255).astype(np.uint8))
    cv2.imwrite("flutter_mask.png", (flutter_mask * 255).astype(np.uint8))
    
    print("\n" + "="*60)
    print("Saved comparison images:")
    print("  - gradio_preprocessed.png")
    print("  - flutter_preprocessed.png")
    print("  - gradio_mask.png")
    print("  - flutter_mask.png")
    print("="*60)

if __name__ == "__main__":
    main()
