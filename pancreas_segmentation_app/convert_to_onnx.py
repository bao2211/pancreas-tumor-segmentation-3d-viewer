"""
Convert Keras model to ONNX format for cross-platform deployment
Works on both Windows and Android via ONNX Runtime
"""
import os
import sys

# Set environment to avoid TF warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import tf2onnx
import numpy as np

def main():
    # Model paths
    keras_model_path = r"I:\My Drive\Colab Notebooks\Gradio Web App\unet_best.keras"
    onnx_output_path = r"C:\Users\Admin\Documents\pancreas_segmentation_app\assets\models\unet_model.onnx"
    
    print("=" * 50)
    print("Keras to ONNX Converter")
    print("=" * 50)
    
    # Check if model exists
    if not os.path.exists(keras_model_path):
        print("[ERROR] Model not found:", keras_model_path)
        sys.exit(1)
    
    print("\n[INFO] Loading model:", keras_model_path)
    
    # Load the Keras model (no custom objects needed with compile=False)
    try:
        model = tf.keras.models.load_model(
            keras_model_path,
            compile=False
        )
        print("[OK] Model loaded successfully!")
    except Exception as e:
        print("[ERROR] Error loading model:", e)
        sys.exit(1)
    
    # Print model info
    print("\n[INFO] Model Info:")
    print("   Input shape:", model.input_shape)
    print("   Output shape:", model.output_shape)
    
    # Define input signature for ONNX conversion
    # Model expects (batch, 128, 128, 1) - grayscale CT slices
    input_signature = [tf.TensorSpec(shape=(1, 128, 128, 1), dtype=tf.float32, name='input')]
    
    print("\n[INFO] Converting to ONNX...")
    
    try:
        # Convert to ONNX
        model_proto, _ = tf2onnx.convert.from_keras(
            model,
            input_signature=input_signature,
            opset=13,  # ONNX opset version
            output_path=onnx_output_path
        )
        
        # Get file size
        file_size = os.path.getsize(onnx_output_path) / (1024 * 1024)
        
        print("\n[OK] ONNX model saved!")
        print("   Path:", onnx_output_path)
        print("   Size:", round(file_size, 2), "MB")
        
    except Exception as e:
        print("[ERROR] Conversion error:", e)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Verify the model
    print("\n[INFO] Verifying ONNX model...")
    try:
        import onnxruntime as ort
        
        # Load and test inference
        session = ort.InferenceSession(onnx_output_path)
        
        # Get input/output info
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        output_name = session.get_outputs()[0].name
        output_shape = session.get_outputs()[0].shape
        
        print("   Input:", input_name, "- shape", input_shape)
        print("   Output:", output_name, "- shape", output_shape)
        
        # Test inference with dummy data
        dummy_input = np.random.randn(1, 128, 128, 1).astype(np.float32)
        output = session.run(None, {input_name: dummy_input})
        
        print("   Test inference output shape:", output[0].shape)
        print("\n[OK] ONNX model verified successfully!")
        
    except Exception as e:
        print("[WARNING] Verification warning:", e)
    
    print("\n" + "=" * 50)
    print("[DONE] Conversion complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
