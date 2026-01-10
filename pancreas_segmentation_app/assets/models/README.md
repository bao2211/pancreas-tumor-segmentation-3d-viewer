# Placeholder for TFLite Model

Place your converted `unet_model.tflite` file here.

## How to convert your Keras model:

```python
import tensorflow as tf

# Define your custom objects (loss functions, metrics)
def dice_loss_focus(y_true, y_pred):
    # Your implementation
    pass

def dice_tumor(y_true, y_pred):
    # Your implementation
    pass

# Load your Keras model
model = tf.keras.models.load_model(
    'path/to/unet_best.keras',
    custom_objects={
        'dice_loss_focus': dice_loss_focus,
        'dice_tumor': dice_tumor,
    }
)

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Optional: Enable optimization for smaller model size
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
tflite_model = converter.convert()

# Save the model
with open('unet_model.tflite', 'wb') as f:
    f.write(tflite_model)

print("Model converted successfully!")
```

## Expected model specifications:

- **Input shape**: (1, 128, 128, 1)
- **Output shape**: (1, 128, 128, 2)
- **Input type**: float32
- **Output type**: float32
