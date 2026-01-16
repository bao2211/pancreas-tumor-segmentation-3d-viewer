# Professional UI User Guide

## 🎯 Overview

The enhanced interface provides a clinical-grade analysis environment with comprehensive statistics, model transparency, and professional visualizations.

## 📊 Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  🧬 Pancreas Tumor Detection System     [Settings]              │
│     AI-Powered NIfTI CT Analysis                                │
├──────────────┬──────────────┬──────────────────────────────────┤
│              │              │                                   │
│   LEFT       │   MIDDLE     │         RIGHT                     │
│   PANEL      │   PANEL      │         PANEL                     │
│              │              │                                   │
│  • File Info │  • Slice     │  • Image Viewer                   │
│  • Controls  │    Navigator │  • Zoom/Pan                       │
│  • Model     │  • Status    │  • Overlay                        │
│    Info      │    Icons     │  • Legend                         │
│  • Stats     │              │                                   │
│              │              │                                   │
│ (Scrollable) │  (List)      │  (Interactive)                    │
└──────────────┴──────────────┴──────────────────────────────────┘
```

## 🔍 Left Panel Features

### 1. **File Information Card**
- **File Name**: Displays the loaded NIfTI file
- **Dimensions**: Shows volume size (e.g., 512 × 512 × 100)
- **Total Slices**: Number of slices in the CT scan
- **Scan Progress**: Real-time progress of analysis

**Visual Cue**: Gradient blue background with medical information icon

### 2. **Analysis Controls**
- **Run Full Scan**: Initiates two-stage AI analysis on all slices
  - Shows "Scanning..." with progress during analysis
  - Disabled while scanning to prevent multiple runs
- **Load New Scan**: Clear current scan and load a new file

### 3. **Model Information Card** 🤖

Always visible for transparency:

#### Architecture
- **Two-Stage U-Net**
  - Stage 1: Pancreas Detection (256×256)
  - Stage 2: Tumor Detection (128×128 ROI)

#### Preprocessing
- **HU Windowing [-128, 127]**
  - Hounsfield Unit normalization to [0, 1]
  - ROI cropping for tumor detection

#### Enhancement
- **Context-Aware Prediction**
  - Temporal smoothing across slices
  - Morphological operations for continuity
  - Connected component analysis

#### Training Dataset
- **MSD Task07 Pancreas**

### 4. **Statistics Dashboard** 📈

*Appears after full scan completion*

#### **Overall Summary**
```
┌─────────────────────────────────────────┐
│ ⚠️  Tumor Detected                      │
│ Suspicious regions identified in        │
│ 12 slice(s)                             │
│                                         │
│ ⓘ AI-assisted detection: Requires      │
│   clinical validation                   │
└─────────────────────────────────────────┘
```

#### **Volume Information**
- **Dimensions**: 3D volume size
- **Total Slices**: Full dataset size
- **Scanned Slices**: Completed analysis count

#### **Pancreas Detection**
- **Slices with Pancreas**: Count and percentage
- **Progress Bar**: Visual representation
- **Total Pancreas Pixels**: Cumulative detection

#### **Tumor Analysis** ⚠️

**Primary Metric - Tumor Burden**
```
┌─────────────────────────────────────────┐
│ Tumor Burden              12.45%        │
│ Percentage of tumor relative to         │
│ pancreas tissue                         │
└─────────────────────────────────────────┘
```

- **Affected Slices**: Tumor-positive slices with percentage
- **Total Tumor Pixels**: Cumulative tumor detection
- **Avg Tumor per Slice**: Average pixels in affected slices
- **Max Tumor in Slice**: Peak tumor with location (e.g., "Slice 45")

## 🗂️ Middle Panel - Slice Navigator

### Slice List Features

Each slice entry shows:
- **Slice Number**: Sequential index
- **Status Icon**:
  - 🟢 Green check: Pancreas detected, no tumor
  - 🟠 Orange warning: Tumor detected
  - ⚪ Gray circle: No pancreas or not scanned
- **Status Text**: "Tumor detected", "Pancreas only", or "No pancreas"

### Interaction
- **Click** any slice to jump to it in the viewer
- **Selected slice** highlighted in blue
- **Scroll** through all slices easily

## 🖼️ Right Panel - Slice Viewer

### Image Display
- **Full-size CT slice** with professional overlay
- **Zoom/Pan** using mouse wheel and drag
- **Black background** for medical imaging standard

### Overlay System
- **Cyan outline**: Pancreas boundary
- **Red outline**: Tumor boundary
- **Original image**: Grayscale CT data

### Information Footer

Displayed on scanned slices:
```
┌─────────────────────────────────────────┐
│ Slice 45 - ⚠️ Tumor detected            │
│                                         │
│ □ Pancreas (1,234 pixels)               │
│ □ Tumor (156 pixels)                    │
└─────────────────────────────────────────┘
```

## 🎨 Color Coding System

| Color | Meaning | Usage |
|-------|---------|-------|
| 🟦 Blue | Primary/Information | Headers, buttons, primary UI |
| 🟩 Green | Success/Normal | Pancreas without tumor |
| 🟧 Orange | Warning/Tumor | Tumor detection alerts |
| 🟥 Red | Critical/Tumor | Tumor outlines in images |
| 🔵 Cyan | Pancreas | Pancreas outlines in images |
| ⚪ Gray | Neutral/Inactive | Unscanned or empty slices |

## 📖 Clinical Interpretation Guide

### Understanding Tumor Burden

**Tumor Burden** is the most important metric:
- **< 5%**: Small tumor, early stage potential
- **5-20%**: Moderate involvement
- **> 20%**: Significant tumor burden

### Workflow for Clinicians

1. **Initial Review**
   - Check "Tumor Detected" status
   - Note tumor burden percentage
   - Review affected slice count

2. **Distribution Analysis**
   - Use "Affected Slices" percentage to understand spread
   - Check "Max Tumor in Slice" for peak location
   - Navigate to that slice for detailed review

3. **Slice-by-Slice Examination**
   - Click through orange-highlighted slices
   - Zoom in on tumor regions
   - Assess boundary clarity and size

4. **Clinical Correlation**
   - Compare with patient symptoms
   - Review with radiological findings
   - Note: AI assists but doesn't replace clinical judgment

## ⚙️ Advanced Features

### Server Settings
- Click **Settings** icon in header
- Configure Python backend URL
- Default: `http://localhost:8765`
- For remote: Use IP address (e.g., `http://192.168.1.100:8765`)

### Scan Progress
- Real-time progress bar in status bar
- Shows percentage and current/total slices
- Context-aware processing ensures continuity

## 🚨 Important Notes

### Clinical Disclaimer
> **AI-assisted detection requires clinical validation**
> 
> Results are meant to assist, not replace, clinical diagnosis. 
> Always correlate with:
> - Patient history
> - Physical examination  
> - Other imaging modalities
> - Laboratory findings

### Technical Limitations
- **2D Analysis**: Processes slice-by-slice, not full 3D
- **Binary Classification**: Detects presence, not stage/grade
- **No Size Measurements**: Pixel counts, not mm/cm
- **Context Window**: Limited to adjacent slices (3-slice buffer)

## 🎯 Quick Actions

| Action | How To |
|--------|--------|
| Load Scan | Click "Load NIfTI File" FAB or "Load New Scan" |
| Start Analysis | Click "Run Full Scan" |
| Jump to Tumor | Click orange slice in navigator |
| Zoom Image | Mouse wheel on right panel |
| Pan Image | Click and drag on right panel |
| View Stats | Scroll left panel after scan |
| Change Server | Click Settings icon |

## 📱 Keyboard Shortcuts

*Coming soon in future updates*

## 💡 Tips for Best Results

1. **Complete Scans**: Always run full scan for accurate statistics
2. **Review Context**: Check slices before and after tumor detections
3. **Zoom Carefully**: Use zoom to verify boundary accuracy
4. **Compare Metrics**: Cross-reference tumor burden with slice distribution
5. **Document Findings**: Note slice numbers for reporting

## 🔄 Updates & Maintenance

### Version Information
- **Current Version**: 2.0 Professional UI
- **Release Date**: January 2026
- **Compatible With**: Chrome, Firefox, Edge browsers

### What's New in 2.0
- ✨ Professional three-column layout
- 📊 Comprehensive statistics dashboard
- 🤖 Model information transparency
- 📈 Tumor burden primary metric
- 🎨 Enhanced visual design
- 🔍 Improved slice navigation

---

## 📞 Support

For technical issues or questions:
- Check server connection in Settings
- Verify Python backend is running
- Review `PROFESSIONAL_UI_UPGRADE_SUMMARY.md` for technical details

---

**Remember**: This tool assists healthcare professionals in preliminary tumor detection. Always combine AI insights with clinical expertise for patient care decisions.
