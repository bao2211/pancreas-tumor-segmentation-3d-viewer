"""
Model Conversion Script: Keras (.keras) to TensorFlow Lite (.tflite)

This script converts your trained pancreas segmentation model to TFLite format
for use in the Flutter mobile/desktop app.

Usage:
    python convert_model_to_tflite.py

Requirements:
    pip install tensorflow
"""

import tensorflow as tf
import numpy as np
import os

# ============================================
# CONFIGURATION
# ============================================

# Path to your trained Keras model
KERAS_MODEL_PATH = "../Gradio Web App/unet_best.keras"

# Output path for TFLite model
TFLITE_OUTPUT_PATH = "assets/models/unet_model.tflite"

# ============================================
# CUSTOM LOSS FUNCTIONS (required for loading)
# ============================================

def dice_loss_focus(y_true, y_pred, smooth=1e-6):
    """Dice loss focusing on foreground classes"""
    y_true = tf.cast(y_true, tf.float32)
    y_true_fg = y_true[..., 1:]
    y_pred_fg = y_pred[..., 1:]
    inter = tf.reduce_sum(y_true_fg * y_pred_fg, axis=[1,2,3])
    union = tf.reduce_sum(y_true_fg + y_pred_fg, axis=[1,2,3])
    dice = (2. * inter + smooth) / (union + smooth)
    return 1. - tf.reduce_mean(dice)


def dice_tumor(y_true, y_pred, smooth=1e-6):
    """Dice coefficient for tumor class (metric)"""
    y_true = tf.cast(y_true, tf.float32)
    y_true_t = y_true[..., 1] if y_true.shape[-1] == 2 else y_true[..., 2]
    y_pred_t = y_pred[..., 1] if y_pred.shape[-1] == 2 else y_pred[..., 2]
    inter = tf.reduce_sum(y_true_t * y_pred_t, axis=[1,2])
    union = tf.reduce_sum(y_true_t + y_pred_t, axis=[1,2])
    return tf.reduce_mean((2.*inter + smooth)/(union + smooth))


def cce_plus_dice_loss_safe(y_true, y_pred, smooth=1e-6):
    """Combined Categorical Cross-Entropy + Dice Loss"""
    y_true = tf.cast(y_true, tf.float32)
    
    # Categorical Cross-Entropy
    cce = tf.keras.losses.categorical_crossentropy(y_true, y_pred)
    cce = tf.reduce_mean(cce)
    
    # Dice Loss for foreground
    y_true_fg = y_true[..., 1:]
    y_pred_fg = y_pred[..., 1:]
    inter = tf.reduce_sum(y_true_fg * y_pred_fg, axis=[1,2,3])
    union = tf.reduce_sum(y_true_fg + y_pred_fg, axis=[1,2,3])
    dice = (2. * inter + smooth) / (union + smooth)
    dice_loss = 1. - tf.reduce_mean(dice)
    
    return cce + dice_loss


def dice_coef(y_true, y_pred, smooth=1e-6):
    """General Dice coefficient"""
    y_true = tf.cast(y_true, tf.float32)
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)


# ============================================
# MAIN CONVERSION
# ============================================

def convert_model():
    print("=" * 50)
    print("KERAS TO TFLITE MODEL CONVERSION")
    print("=" * 50)
    
    # Check if Keras model exists
    if not os.path.exists(KERAS_MODEL_PATH):
        print(f"\n❌ ERROR: Model not found at {KERAS_MODEL_PATH}")
        print("Please update KERAS_MODEL_PATH to point to your model.")
        return False
    
    print(f"\n📂 Loading model from: {KERAS_MODEL_PATH}")
    
    try:
        # Load the Keras model with custom objects
        model = tf.keras.models.load_model(
            KERAS_MODEL_PATH,
            custom_objects={
                'dice_loss_focus': dice_loss_focus,
                'dice_tumor': dice_tumor,
                'cce_plus_dice_loss_safe': cce_plus_dice_loss_safe,
                'dice_coef': dice_coef,
            },
            compile=False  # Don't need to compile for inference
        )
        print("✅ Model loaded successfully!")
        
        # Print model summary
        print("\n📋 Model Summary:")
        print(f"   Input shape:  {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
        
    except Exception as e:
        print(f"\n❌ Failed to load model: {e}")
        return False
    
    # Convert to TFLite
    print("\n🔄 Converting to TFLite format...")
    print("   (Using TF Select ops for complex model layers)")
    
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        # Enable TF Select ops for complex operations
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,  # Standard TFLite ops
            tf.lite.OpsSet.SELECT_TF_OPS      # TensorFlow ops (for complex layers)
        ]
        
        # Allow custom ops
        converter._experimental_lower_tensor_list_ops = False
        
        # Optional: Use float16 quantization for smaller model
        # converter.optimizations = [tf.lite.Optimize.DEFAULT]
        # converter.target_spec.supported_types = [tf.float16]
        
        tflite_model = converter.convert()
        print("✅ Conversion successful!")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        return False
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(TFLITE_OUTPUT_PATH), exist_ok=True)
    
    # Save the TFLite model
    print(f"\n💾 Saving to: {TFLITE_OUTPUT_PATH}")
    
    with open(TFLITE_OUTPUT_PATH, 'wb') as f:
        f.write(tflite_model)
    
    # Print file size
    file_size_mb = os.path.getsize(TFLITE_OUTPUT_PATH) / (1024 * 1024)
    print(f"✅ Model saved! Size: {file_size_mb:.2f} MB")
    
    # Verify the converted model
    print("\n🔍 Verifying converted model...")
    
    try:
        interpreter = tf.lite.Interpreter(model_path=TFLITE_OUTPUT_PATH)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"   Input:  {input_details[0]['shape']} ({input_details[0]['dtype']})")
        print(f"   Output: {output_details[0]['shape']} ({output_details[0]['dtype']})")
        
        # Test inference
        test_input = np.random.rand(1, 128, 128, 1).astype(np.float32)
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])
        
        print(f"   Test output shape: {output.shape}")
        print("✅ Model verification passed!")
        
    except Exception as e:
        print(f"⚠️ Verification warning: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 CONVERSION COMPLETE!")
    print("=" * 50)
    print(f"\nYour TFLite model is ready at:")
    print(f"   {os.path.abspath(TFLITE_OUTPUT_PATH)}")
    print("\nNext steps:")
    print("1. Copy this file to your Flutter app's assets/models/ folder")
    print("2. Run 'flutter pub get'")
    print("3. Build and run your app!")
    
    return True


if __name__ == "__main__":
    convert_model()
