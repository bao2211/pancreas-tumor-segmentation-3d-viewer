# Multi-Platform Integration for Pancreas Segmentation & Cancerous Tumor Detection

A **multi-platform medical-imaging application** that detects and visualizes pancreatic tumors in CT scans. A **two-stage deep-learning pipeline** first segments the pancreas, then detects tumors inside it, with **context-aware smoothing** across slices and **interactive 3D visualization** — all driven from a single Flutter codebase (Web, Windows, Android) talking to a lightweight Python inference server.

> ⚠️ Research / educational project. **Not a certified medical device** — do not use for clinical diagnosis.

## Highlights

- **Two-stage segmentation** — Pancreas U-Net (256×256) → Tumor U-Net (128×128) for higher accuracy than single-pass models
- **Context-aware prediction** — temporal smoothing across adjacent slices improves tumor connectivity
- **Interactive 3D visualization** — hybrid volume rendering of the CT + surface meshes (marching cubes) of the pancreas/tumor, exported as GLB and explorable in-browser
- **Cross-platform UI** — one Flutter app runs on **Web (Chrome)**, **Windows desktop**, and **Android**
- **NIfTI-native** — accepts `.nii` / `.nii.gz` CT volumes (MSD Task 07 format)
- **Real-time clinical panel** — slice statistics, tumor-volume metrics, and model information in the UI

## Architecture

```
┌──────────────────────────────────────┐
│   Flutter App (Dart) — any platform  │
│  file picker · slice viewer+overlays │
│  3D volume viewer · stats panel      │
└──────────────┬───────────────────────┘
               │ HTTP (JSON + base64) :8765
               ▼
┌──────────────────────────────────────┐
│   Python Inference Server            │
│  two-stage U-Net · temporal context  │
│  marching cubes · volume export      │
└───────┬──────────────────┬───────────┘
        ▼                  ▼
  Pancreas Model      Tumor Model
   (256×256)           (128×128)
```

**Stack:** Flutter/Dart (provider, http, file_picker) · Python (TensorFlow/Keras ≥2.10, nibabel, OpenCV, scikit-image, trimesh, numpy-stl, pyfqmr) · 3D rendering via WebGL (GLB/glTF) · Git LFS for model weights.

## Repository Structure

```
├── pancreas_segmentation_app/   # The application
│   ├── lib/                     # Flutter UI (screens, services, widgets, theme)
│   ├── nii_inference_server.py  # Python backend (two-stage pipeline, port 8765)
│   ├── requirements_nii.txt     # Python dependencies
│   ├── pubspec.yaml             # Flutter dependencies
│   ├── web/ · windows/          # Platform runners
│   └── unet_best.keras          # Model weight (Git LFS)
├── Model/                       # unet_best_pancreas.keras · unet_best_tumor.keras (Git LFS)
├── References/                  # Training/eval notebooks (MSD) + PROJECT_SUMMARY.md + 3D docs
├── Research Paper/              # System & 3D-viewer documentation (EN + Vietnamese)
├── Diagram/                     # System-architecture diagrams (DrawIO + images)
└── .github/                     # Copilot instructions
```

## Quick Start

**Prerequisites:** Python 3.7–3.12 · Flutter 3.x · Git LFS ([git-lfs.com](https://git-lfs.com) or `winget install Git.GitLFS`)

```powershell
# 1. Clone (LFS pulls the real model weights — ~570 MB total)
git lfs install
git clone https://github.com/bao2211/MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection.git
cd MultiPlatform-Intergration-For-Panceas-Segmentation-Cancerous-Tumor-Detection\pancreas_segmentation_app

# 2. Python backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements_nii.txt
python nii_inference_server.py        # keep this terminal open — serves :8765

# 3. Flutter frontend (second terminal)
flutter pub get
flutter run -d chrome                 # or: -d windows (needs VS C++ workload) / -d <android-device>
```

If the app shows a white screen on web, restore the web runner: `flutter create --platforms=web .` (does not touch Dart code). Model files showing as 134-byte pointers means `git lfs pull` was skipped.

## API Reference (backend, `http://localhost:8765`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check & model status |
| POST | `/load_nii` | Upload & load a `.nii`/`.nii.gz` scan |
| POST | `/scan_slice` | Predict pancreas+tumor on one slice |
| POST | `/scan_all` | Batch predict all slices (context-aware) |
| POST | `/reset_context` | Reset the temporal context buffer |
| POST | `/generate_3d_model` | Generate 3D mesh from predictions |
| POST | `/generate_volume_data` | Export volume data for the 3D viewer |
| POST | `/export_volume_mesh` | Export CT volume as GLB mesh |

## Dataset & Training

Models were trained on **MSD Task 07 — Pancreas** (Medical Segmentation Decathlon): 285 training scans / 284 label masks / 146 test scans.

```powershell
curl -L -o dataset/Task07_Pancreas.tar "https://msd-for-monai.s3-us-west-2.amazonaws.com/Task07_Pancreas.tar"
tar -xf dataset/Task07_Pancreas.tar -C dataset/
```

Training, preprocessing and evaluation notebooks (data download → preprocessing → training → testing on the MSD test split) live in [`References/`](References/); see also `PROJECT_SUMMARY.md`, `3D_VISUALIZATION_IMPLEMENTATION.md` and `CONTEXT_AWARE_SYSTEM_SUMMARY.md` there for design details.

## Documentation

- **Setup & startup guide** and full system documentation (Vietnamese + English) in [`Research Paper/`](Research%20Paper/)
- **Architecture diagrams** in [`Diagram/`](Diagram/) (editable DrawIO sources + exports)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `git lfs: command not found` | Install Git LFS, re-clone or `git lfs pull` |
| Model files are 134 bytes | They are LFS pointers — run `git lfs pull` |
| App can't reach server | Start `python nii_inference_server.py` first (port 8765) |
| White screen on web | `flutter create --platforms=web .` then re-run |
| `flutter run -d windows` fails | Install Visual Studio with *Desktop development with C++* |
| Out of memory on large NIfTI | Use a smaller scan or more RAM |

## Future Work

Multi-class organ segmentation · GPU-accelerated real-time inference · cloud backend deployment · native iOS/Android · DICOM support · model ensembling · active learning from user feedback.

## Related Project

Brain-tumor counterpart of this system: **Spearhead** (joint lightweight segmentation + classification research) — the same two-stage → single-model research line.

---
*No license file is included yet — all rights reserved by the author unless otherwise stated.*

