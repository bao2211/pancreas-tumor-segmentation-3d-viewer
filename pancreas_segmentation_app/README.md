# Pancreas Tumor Segmentation App

A cross-platform application for pancreas tumor segmentation using deep learning. Built with Flutter for Windows and Android, with a Python inference server for ML processing.

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Android-blue)
![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Step 1: Start the Inference Server](#step-1-start-the-inference-server)
  - [Step 2: Run the App](#step-2-run-the-app)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

---

## Overview

This application performs automatic segmentation of pancreas tumors from CT scan images using a U-Net deep learning model. The detected tumor regions are highlighted with a red overlay on the original image.

**Key Features:**
- 🖥️ Windows desktop application
- 📱 Android mobile application
- 🧠 Deep learning-based tumor detection
- 🎨 Visual tumor overlay with red highlighting
- 📊 Displays tumor pixel count

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter App (UI)                         │
│              Windows Desktop / Android Mobile               │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Request (Image)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python Inference Server                     │
│                   (inference_server.py)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Keras U-Net Model                       │   │
│  │            (unet_best.keras)                         │   │
│  │    Input: 128×128×1  →  Output: 128×128×2           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Response (Mask + Metadata)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Display Results                            │
│         Original Image + Red Tumor Overlay                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

### Python (Inference Server)
- Python 3.10 or higher
- Required packages:
  ```
  tensorflow>=2.10
  keras
  numpy
  pillow
  ```

### Flutter (App)
- Flutter SDK 3.x
- Dart SDK (included with Flutter)
- For Windows: Visual Studio with C++ desktop development
- For Android: Android SDK, Android Studio (optional)

---

## Installation

### 1. Clone/Download the Project

```powershell
git clone https://github.com/bao2211/MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection.git
cd MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection/pancreas_segmentation_app
```

> ⚠️ **Important:** If your project is on **Google Drive** or a cloud-synced folder, Flutter will fail to create symlinks required for Windows builds. You **must** copy the project to a local drive:
> ```powershell
> # Copy project to local drive
> robocopy "path\to\pancreas_segmentation_app" "C:\temp\pancreas_app" /E /XD build .dart_tool
> cd C:\temp\pancreas_app
> flutter clean
> flutter pub get
> flutter run -d windows
> ```

### 2. Install Python Dependencies

```powershell
pip install tensorflow keras numpy pillow opencv-python
```

### 3. Install Flutter Dependencies

```powershell
flutter pub get
```

### 4. Create Windows Platform Files (if missing)

If the `windows/runner` folder is missing, recreate it:
```powershell
flutter create --platforms=windows .
```

### 5. Model File Location

The inference server automatically detects the model file from:
1. `../Gradio Web App/unet_best.keras` (relative to the project)
2. Custom path (can be configured in `inference_server.py`)

The model file `unet_best.keras` is located in the `Gradio Web App` folder of this repository.

---

## Running the Application

### Step 1: Start the Inference Server

**⚠️ IMPORTANT: The inference server must be running before using the app!**

Open a terminal and run:

```powershell
cd pancreas_segmentation_app
python inference_server.py
```

You should see output like:
```
[INFO] Loading model...
[OK] Model loaded!
    Input: (None, 128, 128, 1)
    Output: (None, 128, 128, 2)

[INFO] Inference server running at:
       - Local:   http://localhost:8765
       - Network: http://192.168.x.x:8765
[INFO] Endpoints:
       POST /segment - Run segmentation
       GET  /health  - Health check

[INFO] For Android app, use: http://192.168.x.x:8765
```

**📝 Note the Network IP address** (e.g., `192.168.1.42`) - you'll need this for Android!

---

### Step 2: Run the App

#### Option A: Windows Desktop

```powershell
flutter run -d windows
```

The Windows app automatically connects to `http://localhost:8765`.

#### Option B: Android Device

1. Connect your Android device via USB
2. Enable USB debugging on your phone
3. Run:
   ```powershell

   flutter run -d <device-id>
   ```
   
   To find your device ID:
   ```powershell
   flutter devices
   ```

4. **Configure Server URL on Android:**
   - Tap the **⚙️ Settings** icon (top-right corner)
   - Enter the server URL: `http://<YOUR-PC-IP>:8765`
     - Example: `http://192.168.1.42:8765`
   - Tap **Connect**
   - Status should show "Connected"

#### Option C: Build Android APK

```powershell
cd C:\Users\Admin\Documents\pancreas_segmentation_app
flutter build apk --release
```

The APK will be at:
```
build\app\outputs\flutter-apk\app-release.apk
```

---

## Usage Guide

### Using the App

1. **Ensure the inference server is running** on your PC

2. **Launch the app** (Windows or Android)

3. **Select an image:**
   - Tap the **"Select Image"** button
   - Choose a CT scan slice image (grayscale medical image)

4. **Run segmentation:**
   - Tap the **"Detect Tumor"** button
   - Wait for processing (a few seconds)

5. **View results:**
   - The original image is displayed with tumor regions highlighted in **red**
   - A **yellow outline** marks the tumor boundary
   - The **tumor pixel count** is shown below the image

### Supported Image Formats

- PNG, JPG, JPEG
- Grayscale CT scan images work best
- The model expects HU (Hounsfield Unit) values in range [-128, 127]

### Example Workflow

```
1. Start server:     python inference_server.py
2. Run Windows app:  flutter run -d windows
3. Select CT image
4. Click "Detect Tumor"
5. View segmentation result
```

---

## Troubleshooting

### Server Issues

| Problem | Solution |
|---------|----------|
| `Model not found` | Ensure `unet_best.keras` is in the project folder |
| `Port 8765 in use` | Close other applications using this port or change the port in `inference_server.py` |
| `Module not found` | Install missing packages: `pip install tensorflow keras numpy pillow` |

### Windows App Issues

| Problem | Solution |
|---------|----------|
| `Server not available` | Make sure `inference_server.py` is running |
| `Connection refused` | Check if firewall is blocking port 8765 |
| `Creating symlink failed` | Project is on Google Drive/OneDrive. Copy to local drive (e.g., `C:\temp\`) |
| `runner folder missing` | Run `flutter create --platforms=windows .` to recreate |

### Android App Issues

| Problem | Solution |
|---------|----------|
| `Server not available` | Configure the correct server IP in Settings (⚙️ icon) |
| `Connection refused` | Ensure phone and PC are on the **same WiFi network** |
| `Cannot connect` | Check PC firewall allows incoming connections on port 8765 |
| `Timeout` | Server might be busy; wait and retry |

### Finding Your PC's IP Address

```powershell
ipconfig
```

Look for `IPv4 Address` under your WiFi adapter (e.g., `192.168.1.42`).

### Firewall Configuration

If Android can't connect, you may need to allow Python through the firewall:

1. Open **Windows Defender Firewall**
2. Click **Allow an app through firewall**
3. Click **Change settings** → **Allow another app**
4. Browse to your Python executable and add it
5. Ensure both **Private** and **Public** are checked

---

## Project Structure

```
MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection/
├── Gradio Web App/
│   ├── unet_best.keras        # 🧠 Trained U-Net model
│   └── app_gradio.py          # Original Gradio web app
├── pancreas_segmentation_app/
│   ├── lib/
│   │   ├── main.dart          # App entry point
│   │   ├── screens/
│   │   │   └── home_screen.dart   # Main UI screen
│   │   └── services/
│   │       └── ml_service.dart    # ML service (HTTP client)
│   ├── android/               # Android platform files
│   ├── windows/               # Windows platform files
│   ├── inference_server.py    # Python ML inference server
│   ├── pubspec.yaml           # Flutter dependencies
│   └── README.md              # This file
└── DATA_Pancreas_Segmentation_Bao_fix/
    ├── image/                 # Sample CT scan slices (.npy)
    └── label/                 # Ground truth masks (.npy)
```

---

## Technical Details

### Model Specifications

- **Architecture:** U-Net
- **Input:** 128×128×1 (grayscale)
- **Output:** 128×128×2 (2-class: background, tumor)
- **Preprocessing:** HU windowing [-128, 127] → normalized to [0, 1]

---

## Libraries & Dependencies

### Flutter App Libraries

| Library | Version | Platform | Purpose |
|---------|---------|----------|---------|
| `flutter` | SDK | All | Core UI framework for building cross-platform apps |
| `cupertino_icons` | ^1.0.6 | All | Material Design icons for UI elements |
| `image_picker` | ^1.0.7 | **Android** | Access device camera and photo gallery to select images |
| `file_picker` | ^10.0.0 | **Windows** | Native file browser dialog to select files from disk |
| `image` | ^4.1.7 | All | Image decoding, encoding, and pixel manipulation in Dart |
| `path_provider` | ^2.1.2 | All | Get platform-specific directories (temp, documents, etc.) |
| `path` | ^1.8.3 | All | Cross-platform file path manipulation utilities |
| `provider` | ^6.1.1 | All | State management for reactive UI updates |
| `http` | ^1.6.0 | All | HTTP client for communicating with the inference server |

#### Why Different Libraries for Android vs Windows?

| Feature | Android | Windows | Reason |
|---------|---------|---------|--------|
| **Image Selection** | `image_picker` | `file_picker` | Android uses gallery/camera intents; Windows uses native file dialogs |
| **File Access** | Scoped storage | Full filesystem | Android has restricted file access; Windows allows direct paths |

---

### Python Inference Server Libraries

| Library | Purpose |
|---------|---------|
| `tensorflow` | Deep learning framework - loads and runs the Keras U-Net model |
| `keras` | High-level neural network API (bundled with TensorFlow 2.x) |
| `numpy` | Numerical computing - array operations, image preprocessing |
| `opencv-python` (cv2) | Computer vision - image resizing, color conversion, morphology |
| `pillow` (PIL) | Image I/O - loading/saving PNG, JPG images |
| `http.server` | Python built-in - creates HTTP server for REST API |
| `base64` | Python built-in - encode binary mask as text for JSON response |
| `json` | Python built-in - serialize/deserialize API request/response |

#### Server Data Flow

```
Image (bytes) → PIL.Image → numpy array → cv2 preprocessing 
    → TensorFlow inference → numpy mask → PIL.Image → base64 → JSON
```

---

### Original Gradio Web App Libraries

| Library | Purpose |
|---------|---------|
| `gradio` | Web UI framework - auto-generates interactive ML demo interface |
| `tensorflow` | Deep learning - model loading and inference |
| `numpy` | Array operations - image data manipulation |
| `opencv-python` | Image processing - resize, normalize, color conversion |

#### Gradio vs Flutter Comparison

| Aspect | Gradio Web App | Flutter App |
|--------|----------------|-------------|
| **Deployment** | Web browser only | Native Windows + Android |
| **Installation** | Run Python script | Install APK/EXE |
| **Offline** | ❌ Needs server | ✅ Local server can run offline |
| **Performance** | Browser overhead | Native performance |
| **UI Customization** | Limited (pre-built) | Full control |
| **Distribution** | Share URL | Distribute app file |

---

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/segment` | POST | Run tumor segmentation |

### Segment Request

```http
POST /segment
Content-Type: multipart/form-data

file: <image-file>
```

### Segment Response

```json
{
  "mask": "<base64-encoded-png>",
  "tumor_pixels": 267,
  "total_pixels": 16384,
  "tumor_percentage": 1.63
}
```

---

## Quick Start Summary

```powershell
# Terminal 1 - Start Server
cd pancreas_segmentation_app
python inference_server.py

# Terminal 2 - Run Windows App (in another terminal)
cd pancreas_segmentation_app
flutter run -d windows

# Or run Android App
flutter run -d <your-device-id>
```

**For Android:** Remember to configure the server IP in the app settings! ⚙️

---

## License

This project is for educational and research purposes.
