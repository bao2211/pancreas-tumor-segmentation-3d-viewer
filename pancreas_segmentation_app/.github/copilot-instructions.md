# Pancreas Tumor Segmentation App

## Project Overview
A Flutter cross-platform application for pancreas tumor segmentation using TensorFlow Lite.

## Tech Stack
- **Framework**: Flutter 3.x
- **Language**: Dart
- **ML Runtime**: TensorFlow Lite
- **Platforms**: Android, Windows Desktop

## Key Features
- Upload CT scan images (PNG, JPG)
- TFLite model inference (128x128 input, 2-class output)
- HU windowing preprocessing (clip -128 to 127, normalize to [0,1])
- Segmentation overlay visualization
- Cross-platform support (Android + Windows)

## Project Structure
```
lib/
├── main.dart                 # App entry point
├── screens/
│   └── segmentation_screen.dart
├── services/
│   └── ml_service.dart       # TFLite inference
├── widgets/
│   └── image_overlay.dart    # Overlay visualization
└── utils/
    └── image_processing.dart # Preprocessing utilities
assets/
└── models/
    └── unet_model.tflite     # Place your TFLite model here
```

## Setup Instructions
1. Install Flutter SDK: https://flutter.dev/docs/get-started/install
2. Enable Windows desktop: `flutter config --enable-windows-desktop`
3. Place your `unet_model.tflite` in `assets/models/`
4. Run `flutter pub get`
5. Run `flutter run -d windows` or `flutter run -d android`

## Model Conversion
Convert your Keras model to TFLite:
```python
import tensorflow as tf
model = tf.keras.models.load_model('unet_best.keras', custom_objects={...})
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
with open('assets/models/unet_model.tflite', 'wb') as f:
    f.write(tflite_model)
```
