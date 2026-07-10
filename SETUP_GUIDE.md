# Setup & Startup Guide — Pancreas Tumor Detection System

## 📋 Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.7 – 3.12 | `python --version` |
| Flutter | 3.x | `flutter --version` |
| Dart | 3.x+ | (included with Flutter) |
| Git LFS | 3.x | `git lfs version` |

> **⚠️ Important:** TensorFlow does **not** support Python 3.14+. If `python --version` shows `3.14.x`, you must use Python 3.12 specifically. See Option B below for the easiest way to set this up with `uv`.

---

## 1. Install Python Dependencies

### Option A: Using venv (recommended)

```powershell
# Navigate to the app directory
cd pancreas_segmentation_app

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements_nii.txt
```

### Option B: Using uv (recommended — handles Python versions automatically)

```powershell
cd pancreas_segmentation_app
pip install uv
uv venv --python 3.12
uv pip install -r requirements_nii.txt
```

**`requirements_nii.txt` contents:**
```
tensorflow>=2.10.0
numpy>=1.23.0
opencv-python>=4.7.0
Pillow>=9.5.0
nibabel>=5.0.0
scikit-image>=0.21.0
trimesh>=3.23.0
numpy-stl>=3.0.0
pyfqmr>=0.1.5
```

---

## 2. Install Flutter Dependencies

```powershell
cd pancreas_segmentation_app
flutter pub get
```

**Key Flutter packages** (from `pubspec.yaml`):
- `provider` — State management
- `http` — HTTP client for API calls
- `file_picker` — File selection dialogs
- `image_picker` — Camera/gallery access
- `path_provider` — File system paths

---

## 3. Get Model Files (Git LFS)

The model files (`unet_best_pancreas.keras`, `unet_best_tumor.keras`) are stored with **Git LFS**. If you cloned the repo without the actual model files (they appear as 134-byte text pointers), run:

```powershell
# Install Git LFS if not already installed
# Windows: https://git-lfs.com/ or `winget install Git.GitLFS`

# From the project root
git lfs install
git lfs pull
```

Expected file sizes after pull:
| File | Size |
|------|------|
| `Model/unet_best_pancreas.keras` | ~200 MB |
| `Model/unet_best_tumor.keras` | ~366 MB |

---

## 4. Add Web Support (First Time Only)

If the `web/` folder lacks `index.html`, `manifest.json`, or icons:

```powershell
cd pancreas_segmentation_app
flutter create --platforms=web .
```

> ⚠️ This only re-creates web-specific files; it **won't** overwrite your Dart code.

---

## 5. Start the Application

### Step 1 — Start the Inference Server

```powershell
cd pancreas_segmentation_app

# Activate the virtual environment (if not already active)
.venv\Scripts\Activate.ps1

# Start the server
python nii_inference_server.py
```

**Expected output:**
```
============================================================
NIfTI CT Scan Inference Server
Two-Stage Pancreas & Tumor Detection
============================================================
[OK] Pancreas model: ...\Model\unet_best_pancreas.keras
[OK] Tumor model: ...\Model\unet_best_tumor.keras
[OK] Models pre-loaded successfully!
[OK] Server running at http://localhost:8765
```

**Available endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check & model status |
| POST | `/load_nii` | Upload & load `.nii`/`.nii.gz` file |
| POST | `/scan_slice` | Predict on a single slice |
| POST | `/scan_all` | Batch predict all slices (context-aware) |
| POST | `/reset_context` | Reset temporal context buffer |
| POST | `/generate_3d_model` | Generate 3D mesh from predictions |
| POST | `/generate_volume_data` | Export volume data for 3D viewer |
| POST | `/export_volume_mesh` | Export CT volume as GLB mesh |

> **Keep this terminal window open** while using the app.

### Step 2 — Run the Flutter App

#### 🖥️ Web (Chrome) — No extra tools needed

```powershell
cd pancreas_segmentation_app
flutter run -d chrome
```

#### 🪟 Windows Desktop — Requires Visual Studio

```powershell
# Requires Visual Studio with "Desktop development with C++" workload
flutter run -d windows
```

#### 📱 Android — Requires Android SDK

```powershell
# Connect your device via USB (debugging enabled)
flutter devices          # Find your device ID
flutter run -d <device-id>
```

#### 📦 Build Android APK (standalone)

```powershell
flutter build apk --release
# Output: build\app\outputs\flutter-apk\app-release.apk
```

---

## 6. Using the App

1. **Ensure the inference server is running** (port 8765)
2. **Launch the Flutter app** (Chrome, Windows, or Android)
3. Click **"Select NIfTI File"** and choose a `.nii` or `.nii.gz` file from the dataset
4. After loading, click **"Scan All Slices"** to run the two-stage pancreas → tumor detection
5. Navigate slices with the slider to view pancreas (cyan) and tumor (red) overlays
6. Use **"Generate 3D Model"** to create an interactive 3D visualization

---

## 7. Dataset

The models were trained on **MSD Task 07 — Pancreas** (Medical Segmentation Decathlon).

```powershell
# Download (11.4 GB)
curl -L -o dataset/Task07_Pancreas.tar `
  "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task07_Pancreas.tar"

# Extract
tar -xf dataset/Task07_Pancreas.tar -C dataset/
```

| Split | Contents | Count |
|-------|----------|-------|
| `dataset/Task07_Pancreas/imagesTr/` | Training CT scans | 285 files |
| `dataset/Task07_Pancreas/labelsTr/` | Training masks | 284 files |
| `dataset/Task07_Pancreas/imagesTs/` | Test CT scans | 146 files |

---

## 🧠 Architecture Overview

```
┌──────────────────────────────────────┐
│        Flutter App (Dart)            │
│  - File picker for .nii/.nii.gz      │
│  - Slice viewer with overlays        │
│  - 3D volume visualization (Three.js)│
│  - Real-time statistics panel        │
└──────────────┬───────────────────────┘
               │ HTTP (JSON + base64)
               ▼
┌──────────────────────────────────────┐
│    Python Inference Server           │
│  - Two-stage U-Net pipeline          │
│  - Context-aware temporal smoothing  │
│  - 3D mesh generation (marching cubes)│
│  - Volume rendering data export      │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────┐     ┌──────────────┐
│ Pancreas │     │ Tumor Model  │
│ Model    │────▶│ (128×128)    │
│(256×256) │     └──────────────┘
└──────────┘
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `git lfs` not found | Install from https://git-lfs.com or `winget install Git.GitLFS` |
| Model files are 134 bytes | Run `git lfs pull` to download actual models |
| `flutter: command not found` | Add Flutter SDK `bin` folder to your PATH |
| `flutter run -d windows` fails | Install Visual Studio with "Desktop development with C++" |
| `Server not reachable` in app | Make sure the Python inference server is running on port 8765 |
| Out of memory loading large NIfTI | Use a smaller CT scan or upgrade RAM |
| Web app shows white screen | Run `flutter create --platforms=web .` to restore missing web files |
