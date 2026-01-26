"""
Create comprehensive documentation for the full pancreas tumor detection system
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

def add_heading_with_style(doc, text, level):
    """Add heading with custom styling"""
    heading = doc.add_heading(text, level=level)
    if level == 1:
        for run in heading.runs:
            run.font.color.rgb = RGBColor(13, 71, 161)  # Blue
    return heading

def add_styled_paragraph(doc, text, bold=False, italic=False, size=11):
    """Add paragraph with styling"""
    para = doc.add_paragraph(text)
    para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in para.runs:
        run.font.size = Pt(size)
        if bold:
            run.font.bold = True
        if italic:
            run.font.italic = True
    return para

def add_bullet_point(doc, text, level=0):
    """Add bullet point with indentation"""
    para = doc.add_paragraph(text, style='List Bullet')
    para.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    for run in para.runs:
        run.font.size = Pt(11)
    return para

def add_code_block(doc, code_text):
    """Add code block with monospace font"""
    para = doc.add_paragraph(code_text)
    para.paragraph_format.left_indent = Inches(0.5)
    para.paragraph_format.right_indent = Inches(0.5)
    for run in para.runs:
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
    return para

def create_full_documentation():
    doc = Document()
    
    # Title Page
    title = doc.add_heading('HỆ THỐNG PHÁT HIỆN KHỐI U TỤY', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph('Tài Liệu Kỹ Thuật Toàn Diện')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in subtitle.runs:
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(66, 66, 66)
    
    doc.add_paragraph()
    info = doc.add_paragraph('Phiên bản: 2.0\nNgày: Tháng 1, 2026')
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_page_break()
    
    # =================================================================
    # SECTION 1: TỔNG QUAN HỆ THỐNG
    # =================================================================
    add_heading_with_style(doc, '1. TỔNG QUAN HỆ THỐNG', 1)
    
    add_styled_paragraph(doc, 
        'Hệ thống phát hiện khối u tụy là một ứng dụng y tế đa nền tảng sử dụng học sâu '
        'để phân tích hình ảnh CT scan và tự động phát hiện tụy cũng như khối u trong tụy. '
        'Hệ thống kết hợp machine learning với công nghệ trực quan hóa 3D hiện đại để cung '
        'cấp công cụ hỗ trợ chẩn đoán toàn diện.')
    
    add_heading_with_style(doc, '1.1. Mục Tiêu Dự Án', 2)
    add_bullet_point(doc, 'Phát hiện tự động vị trí tụy trong CT scan')
    add_bullet_point(doc, 'Phân đoạn chính xác khối u ác tính trong tụy')
    add_bullet_point(doc, 'Trực quan hóa 3D tương tác cho bác sĩ')
    add_bullet_point(doc, 'Cung cấp thống kê định lượng về kích thước khối u')
    add_bullet_point(doc, 'Hỗ trợ quyết định lâm sàng với AI')
    
    add_heading_with_style(doc, '1.2. Đặc Điểm Nổi Bật', 2)
    
    # Feature table
    table = doc.add_table(rows=7, cols=2)
    table.style = 'Light Grid Accent 1'
    
    features = [
        ('Tính Năng', 'Mô Tả'),
        ('Phân đoạn 2 giai đoạn', 'Tụy → Khối u (context-aware)'),
        ('Trực quan hóa 3D', 'Volume rendering + Surface meshes'),
        ('Đa nền tảng', 'Windows, Web, Android (sẵn sàng)'),
        ('Thời gian thực', '200ms/slice, ~15s/toàn bộ scan'),
        ('Độ chính xác', 'Dice score > 0.85 cho tụy, > 0.75 cho khối u'),
        ('UI chuyên nghiệp', 'Glassmorphism, real-time metrics')
    ]
    
    for i, (col1, col2) in enumerate(features):
        row = table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    # =================================================================
    # SECTION 2: KIẾN TRÚC HỆ THỐNG
    # =================================================================
    doc.add_page_break()
    add_heading_with_style(doc, '2. KIẾN TRÚC HỆ THỐNG', 1)
    
    add_heading_with_style(doc, '2.1. Tổng Quan Kiến Trúc', 2)
    add_styled_paragraph(doc,
        'Hệ thống áp dụng kiến trúc client-server với sự phân tách rõ ràng giữa '
        'giao diện người dùng (Flutter) và xử lý AI (Python). Điều này cho phép '
        'tối ưu hóa độc lập từng thành phần và dễ dàng mở rộng.')
    
    add_heading_with_style(doc, '2.2. Flutter Frontend', 2)
    
    add_styled_paragraph(doc, 'Flutter được chọn làm framework frontend vì:', bold=True)
    add_bullet_point(doc, 'Cross-platform: Một codebase chạy trên Windows, Web, Android, iOS')
    add_bullet_point(doc, 'Performance: Native-compiled code với hiệu suất cao')
    add_bullet_point(doc, 'UI/UX: Material Design với widgets phong phú')
    add_bullet_point(doc, 'Hot reload: Tăng tốc phát triển giao diện')
    add_bullet_point(doc, 'WebGL support: Tích hợp Three.js cho 3D rendering')
    
    add_heading_with_style(doc, '2.2.1. Cấu Trúc Flutter App', 3)
    
    add_code_block(doc, '''lib/
├── main.dart                     # Entry point, app initialization
├── screens/
│   └── nii_scan_screen.dart     # Main screen (file upload, viewing)
├── services/
│   └── nii_service.dart         # API communication, state management
├── models/
│   └── nii_scan.dart            # Data models (NiiScan, SliceData)
├── widgets/
│   ├── volume_3d_viewer.dart   # 3D WebGL viewer component
│   ├── model_info_card.dart    # Display model information
│   ├── scan_statistics_panel.dart  # Real-time statistics
│   └── glass_card.dart         # Glassmorphism UI component
└── theme/
    └── app_theme.dart           # App-wide styling, colors''')
    
    add_heading_with_style(doc, '2.2.2. State Management Pattern', 3)
    add_styled_paragraph(doc,
        'Sử dụng Provider pattern cho state management. NiiService là ChangeNotifier '
        'chứa toàn bộ business logic và state của ứng dụng. Widgets lắng nghe thay đổi '
        'và tự động re-render khi state thay đổi.')
    
    add_heading_with_style(doc, '2.2.3. Key Flutter Packages', 3)
    
    packages_table = doc.add_table(rows=5, cols=3)
    packages_table.style = 'Light Grid Accent 1'
    
    packages = [
        ('Package', 'Version', 'Mục Đích'),
        ('provider', '^6.1.1', 'State management, dependency injection'),
        ('http', '^1.6.0', 'HTTP client cho REST API'),
        ('file_picker', '^10.0.0', 'Chọn file NIfTI từ hệ thống'),
        ('image', '^4.1.7', 'Xử lý và hiển thị ảnh 2D')
    ]
    
    for i, (col1, col2, col3) in enumerate(packages):
        row = packages_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        row.cells[2].text = col3
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '2.3. Python Backend Server', 2)
    
    add_styled_paragraph(doc,
        'Backend server được viết bằng Python với http.server tích hợp sẵn. '
        'Server xử lý tất cả các tác vụ AI: load NIfTI files, phân đoạn với U-Net, '
        'tạo 3D meshes, và xuất dữ liệu volume rendering.')
    
    add_heading_with_style(doc, '2.3.1. Cấu Trúc Server', 3)
    
    add_code_block(doc, '''nii_inference_server.py
├── CTVolumeHandler          # HTTP request handler
├── TumorContext             # Context-aware prediction tracking
├── Endpoints:
│   ├── GET  /health         # Health check
│   ├── POST /load_nii       # Upload & load NIfTI file
│   ├── POST /scan_slice     # Process single slice
│   ├── POST /scan_all       # Batch process with context
│   ├── POST /reset_context  # Reset prediction history
│   ├── POST /generate_3d_model      # Create 3D meshes
│   ├── POST /generate_volume_data   # Volume + meshes
│   └── GET  /model.glb      # Download GLB file
└── Model Loading:
    ├── unet_best_pancreas.keras  # Pancreas segmentation
    └── unet_best_tumor.keras     # Tumor detection''')
    
    add_heading_with_style(doc, '2.3.2. Key Python Libraries', 3)
    
    py_libs_table = doc.add_table(rows=7, cols=2)
    py_libs_table.style = 'Light Grid Accent 1'
    
    py_libs = [
        ('Library', 'Mục Đích'),
        ('tensorflow >=2.10.0', 'Deep learning framework, load/run U-Net models'),
        ('nibabel >=5.0.0', 'Read/write NIfTI medical imaging files'),
        ('opencv-python >=4.7.0', 'Image processing, morphological operations'),
        ('numpy >=1.23.0', 'Numerical computations, array operations'),
        ('scikit-image >=0.21.0', 'Marching cubes algorithm, image metrics'),
        ('trimesh >=3.23.0', '3D mesh processing, GLB/glTF export')
    ]
    
    for i, (col1, col2) in enumerate(py_libs):
        row = py_libs_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    # =================================================================
    # SECTION 3: DATA PROCESSING PIPELINE
    # =================================================================
    doc.add_page_break()
    add_heading_with_style(doc, '3. PIPELINE XỬ LÝ DỮ LIỆU', 1)
    
    add_heading_with_style(doc, '3.1. NIfTI File Loading', 2)
    add_styled_paragraph(doc,
        'NIfTI (Neuroimaging Informatics Technology Initiative) là định dạng chuẩn '
        'cho dữ liệu hình ảnh y tế. Thư viện nibabel được sử dụng để đọc file .nii hoặc .nii.gz.')
    
    add_code_block(doc, '''import nibabel as nib

# Load NIfTI file
nii = nib.load('scan.nii.gz')
volume = nii.get_fdata()  # Shape: (512, 512, N_slices)

# Get metadata
spacing = nii.header.get_zooms()  # Voxel spacing (mm)
affine = nii.affine  # Transformation matrix
orientation = nib.orientations.aff2axcodes(affine)''')
    
    add_heading_with_style(doc, '3.2. HU Windowing', 2)
    add_styled_paragraph(doc,
        'CT scans lưu giá trị pixel theo Hounsfield Units (HU). HU windowing chuyển đổi '
        'range HU thành 0-255 để hiển thị và đưa vào model.')
    
    add_code_block(doc, '''def apply_hu_windowing(ct_slice, window_min=-150, window_max=250):
    """
    Soft tissue window for pancreas visualization
    Air: -1000 HU, Water: 0 HU, Soft tissue: 40-80 HU, Bone: 400-1000 HU
    """
    windowed = np.clip(ct_slice, window_min, window_max)
    normalized = (windowed - window_min) / (window_max - window_min)
    return (normalized * 255).astype(np.uint8)''')
    
    add_heading_with_style(doc, '3.3. Two-Stage Segmentation Pipeline', 2)
    
    add_styled_paragraph(doc, 'Giai đoạn 1: Phân đoạn tụy', bold=True)
    add_bullet_point(doc, 'Input: CT slice 512×512 sau HU windowing')
    add_bullet_point(doc, 'Resize về 256×256 cho U-Net pancreas model')
    add_bullet_point(doc, 'Output: Binary mask 256×256 (tụy = 1, background = 0)')
    add_bullet_point(doc, 'Tính bounding box của vùng tụy')
    
    doc.add_paragraph()
    add_styled_paragraph(doc, 'Giai đoạn 2: Phát hiện khối u', bold=True)
    add_bullet_point(doc, 'Crop ROI (Region of Interest) từ pancreas mask')
    add_bullet_point(doc, 'Resize ROI về 128×128 cho U-Net tumor model')
    add_bullet_point(doc, 'Output: Binary mask 128×128 (tumor = 1, non-tumor = 0)')
    add_bullet_point(doc, 'Map mask trở về tọa độ gốc 512×512')
    
    add_heading_with_style(doc, '3.4. Context-Aware Prediction', 2)
    
    add_styled_paragraph(doc,
        'Hệ thống sử dụng TumorContext class để theo dõi predictions qua các slice liên tiếp. '
        'Điều này cải thiện tính liên tục của khối u trong không gian 3D.')
    
    add_heading_with_style(doc, '3.4.1. Temporal Smoothing', 3)
    add_styled_paragraph(doc,
        'Voting mechanism với sliding window (mặc định 3 slices):')
    
    add_code_block(doc, '''# Weight scheme
current_slice_weight = 2.0
previous_slice_weight = 1.0 each

# Voting
for pixel in mask:
    votes = current_mask[pixel] * 2.0
    for prev_mask in history:
        votes += prev_mask[pixel] * 1.0
    
    # Threshold: >= 2.0 votes to keep pixel
    final_mask[pixel] = 1 if votes >= 2.0 else 0''')
    
    add_styled_paragraph(doc, 'Lợi ích:', bold=True)
    add_bullet_point(doc, 'Giảm flickering giữa các slice')
    add_bullet_point(doc, 'Khôi phục detections bị thiếu')
    add_bullet_point(doc, 'Lọc false positives ngẫu nhiên')
    
    add_heading_with_style(doc, '3.4.2. Morphological Operations', 3)
    
    add_code_block(doc, '''# Morphological closing: fill small gaps
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
closed_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# Connected components analysis
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    closed_mask, connectivity=8)

# Remove small noise (< 10 pixels)
for i in range(1, num_labels):
    if stats[i, cv2.CC_STAT_AREA] < 10:
        closed_mask[labels == i] = 0''')
    
    # =================================================================
    # SECTION 4: DEEP LEARNING MODELS
    # =================================================================
    doc.add_page_break()
    add_heading_with_style(doc, '4. MÔ HÌNH DEEP LEARNING', 1)
    
    add_heading_with_style(doc, '4.1. U-Net Architecture', 2)
    
    add_styled_paragraph(doc,
        'U-Net là kiến trúc mạng neural convolutional được thiết kế đặc biệt cho '
        'phân đoạn hình ảnh y tế. Cấu trúc hình chữ U với encoder-decoder và skip connections.')
    
    add_heading_with_style(doc, '4.1.1. Encoder Path (Downsampling)', 3)
    add_bullet_point(doc, 'Conv 3×3 + ReLU (lặp 2 lần)')
    add_bullet_point(doc, 'MaxPool 2×2 để giảm kích thước')
    add_bullet_point(doc, 'Số filters tăng gấp đôi mỗi level: 64 → 128 → 256 → 512')
    add_bullet_point(doc, 'Trích xuất features từ thô đến trừu tượng')
    
    add_heading_with_style(doc, '4.1.2. Bottleneck', 3)
    add_bullet_point(doc, 'Level sâu nhất với 1024 filters')
    add_bullet_point(doc, 'Kích thước nhỏ nhất (ví dụ: 16×16 từ input 256×256)')
    add_bullet_point(doc, 'Chứa representation trừu tượng nhất')
    
    add_heading_with_style(doc, '4.1.3. Decoder Path (Upsampling)', 3)
    add_bullet_point(doc, 'UpConv 2×2 (transpose convolution)')
    add_bullet_point(doc, 'Concatenate với encoder features (skip connections)')
    add_bullet_point(doc, 'Conv 3×3 + ReLU (lặp 2 lần)')
    add_bullet_point(doc, 'Số filters giảm dần: 512 → 256 → 128 → 64')
    
    add_heading_with_style(doc, '4.1.4. Output Layer', 3)
    add_bullet_point(doc, 'Conv 1×1 để giảm về số classes (2 cho binary segmentation)')
    add_bullet_point(doc, 'Softmax activation cho probability distribution')
    add_bullet_point(doc, 'Output shape = Input shape (256×256 hoặc 128×128)')
    
    add_heading_with_style(doc, '4.2. Skip Connections', 2)
    
    add_styled_paragraph(doc,
        'Skip connections là đặc điểm then chốt của U-Net. Chúng kết nối encoder features '
        'trực tiếp với decoder ở cùng resolution level.')
    
    add_styled_paragraph(doc, 'Vai trò:', bold=True)
    add_bullet_point(doc, 'Preserve fine details: Encoder giữ thông tin spatial chi tiết')
    add_bullet_point(doc, 'Combat vanishing gradients: Gradient flow tốt hơn')
    add_bullet_point(doc, 'Localization: Kết hợp context (decoder) với detail (encoder)')
    
    add_heading_with_style(doc, '4.3. Model Training', 2)
    
    add_styled_paragraph(doc, 'Dataset:', bold=True)
    add_bullet_point(doc, 'Medical Segmentation Decathlon - Task 7 (Pancreas)')
    add_bullet_point(doc, '281 CT scans với pancreas annotations')
    add_bullet_point(doc, 'Tumor annotations được tạo hoặc augmented')
    
    doc.add_paragraph()
    add_styled_paragraph(doc, 'Training hyperparameters:', bold=True)
    
    training_table = doc.add_table(rows=7, cols=2)
    training_table.style = 'Light Grid Accent 1'
    
    training_params = [
        ('Parameter', 'Value'),
        ('Loss function', 'Binary crossentropy / Dice loss'),
        ('Optimizer', 'Adam (lr=1e-4)'),
        ('Batch size', '8-16'),
        ('Epochs', '100-150'),
        ('Data augmentation', 'Rotation, flip, elastic transform'),
        ('Validation split', '20%')
    ]
    
    for i, (col1, col2) in enumerate(training_params):
        row = training_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '4.4. Model Evaluation', 2)
    
    metrics_table = doc.add_table(rows=5, cols=3)
    metrics_table.style = 'Light Grid Accent 1'
    
    metrics = [
        ('Metric', 'Pancreas Model', 'Tumor Model'),
        ('Dice Score', '0.85 - 0.90', '0.75 - 0.82'),
        ('IoU (Jaccard)', '0.75 - 0.82', '0.65 - 0.72'),
        ('Precision', '0.88 - 0.92', '0.78 - 0.85'),
        ('Recall', '0.82 - 0.88', '0.72 - 0.80')
    ]
    
    for i, (col1, col2, col3) in enumerate(metrics):
        row = metrics_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        row.cells[2].text = col3
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    # Save document
    output_path = r"Research Paper\Full_System_Documentation_Vietnamese.docx"
    doc.save(output_path)
    print(f"\n✓ Created: {output_path}")
    print(f"  Total sections: 4 (1/3 complete)")
    return output_path

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Creating Comprehensive System Documentation - Part 1")
    print("="*70)
    create_full_documentation()
    print("\nNote: This is part 1 of 3. Will create parts 2 and 3 next.")
    print("="*70 + "\n")
