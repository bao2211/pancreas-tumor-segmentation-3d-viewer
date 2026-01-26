"""
Create comprehensive documentation Part 2: UI/UX and Frontend Features
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading_with_style(doc, text, level):
    """Add heading with custom styling"""
    heading = doc.add_heading(text, level=level)
    if level == 1:
        for run in heading.runs:
            run.font.color.rgb = RGBColor(13, 71, 161)
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
    """Add bullet point"""
    para = doc.add_paragraph(text, style='List Bullet')
    para.paragraph_format.left_indent = Inches(0.25 * (level + 1))
    for run in para.runs:
        run.font.size = Pt(11)
    return para

def add_code_block(doc, code_text):
    """Add code block"""
    para = doc.add_paragraph(code_text)
    para.paragraph_format.left_indent = Inches(0.5)
    para.paragraph_format.right_indent = Inches(0.5)
    for run in para.runs:
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
    return para

def create_part2():
    # Load existing document
    doc = Document(r"Research Paper\Full_System_Documentation_Vietnamese.docx")
    
    # =================================================================
    # SECTION 5: USER INTERFACE
    # =================================================================
    doc.add_page_break()
    add_heading_with_style(doc, '5. GIAO DIỆN NGƯỜI DÙNG', 1)
    
    add_heading_with_style(doc, '5.1. Thiết Kế UI/UX', 2)
    
    add_styled_paragraph(doc,
        'Giao diện được thiết kế theo xu hướng glassmorphism với sự kết hợp '
        'của Material Design. Màu sắc và typography được chọn lọc để phù hợp '
        'với môi trường y tế chuyên nghiệp.')
    
    add_heading_with_style(doc, '5.1.1. Glassmorphism Design', 3)
    
    add_styled_paragraph(doc, 'Đặc điểm:', bold=True)
    add_bullet_point(doc, 'Semi-transparent backgrounds với backdrop blur')
    add_bullet_point(doc, 'Subtle borders với gradient effects')
    add_bullet_point(doc, 'Layered depth với shadows và highlights')
    add_bullet_point(doc, 'Modern aesthetic phù hợp với medical apps')
    
    add_code_block(doc, '''// Glass Card Widget
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      colors: [
        Colors.white.withOpacity(0.1),
        Colors.white.withOpacity(0.05),
      ],
    ),
    borderRadius: BorderRadius.circular(16),
    border: Border.all(
      color: Colors.white.withOpacity(0.2),
    ),
  ),
  child: BackdropFilter(
    filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
    child: content,
  ),
)''')
    
    add_heading_with_style(doc, '5.1.2. Color Scheme', 3)
    
    color_table = doc.add_table(rows=7, cols=3)
    color_table.style = 'Light Grid Accent 1'
    
    colors = [
        ('Màu', 'Hex Code', 'Mục Đích'),
        ('Primary Blue', '#1976D2', 'Headers, buttons, primary actions'),
        ('Deep Blue', '#0D47A1', 'Accents, highlights'),
        ('Light Blue', '#BBDEFB', 'Backgrounds, cards'),
        ('Red', '#F44336', 'Tumor overlay, warnings'),
        ('Green', '#4CAF50', 'Success states, pancreas'),
        ('Grey', '#9E9E9E', 'Text, borders, disabled states')
    ]
    
    for i, (col1, col2, col3) in enumerate(colors):
        row = color_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        row.cells[2].text = col3
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '5.2. Main Screen Components', 2)
    
    add_heading_with_style(doc, '5.2.1. File Upload Section', 3)
    
    add_bullet_point(doc, 'Elevated button "Chọn File NIfTI" với icon')
    add_bullet_point(doc, 'File picker hỗ trợ .nii và .nii.gz')
    add_bullet_point(doc, 'Display file name và size sau khi chọn')
    add_bullet_point(doc, 'Loading indicator khi upload')
    add_bullet_point(doc, 'Error handling với snackbar messages')
    
    add_heading_with_style(doc, '5.2.2. Slice Navigation', 3)
    
    add_styled_paragraph(doc,
        'Slider cho phép di chuyển qua các slice CT với smooth animation:')
    
    add_code_block(doc, '''Slider(
  value: currentSliceIndex.toDouble(),
  min: 0,
  max: (totalSlices - 1).toDouble(),
  divisions: totalSlices - 1,
  label: 'Slice ${currentSliceIndex + 1}/$totalSlices',
  onChanged: (value) {
    setState(() {
      currentSliceIndex = value.toInt();
    });
    _loadSlice(currentSliceIndex);
  },
)''')
    
    add_styled_paragraph(doc, 'Features:', bold=True)
    add_bullet_point(doc, 'Keyboard shortcuts: Arrow keys để navigate')
    add_bullet_point(doc, 'Mouse wheel support để scroll qua slices')
    add_bullet_point(doc, 'Auto-play mode với adjustable speed')
    add_bullet_point(doc, 'Jump to slice input field')
    
    add_heading_with_style(doc, '5.2.3. Image Viewer', 3)
    
    add_styled_paragraph(doc,
        'Central component hiển thị CT slice với tumor overlay:')
    
    add_bullet_point(doc, 'Responsive sizing: Auto-scale để fit container')
    add_bullet_point(doc, 'Zoom controls: +/- buttons và mouse wheel')
    add_bullet_point(doc, 'Pan capability: Click and drag để di chuyển')
    add_bullet_point(doc, 'Reset view button: Về default zoom/position')
    add_bullet_point(doc, 'Toggle overlay: Show/hide tumor mask')
    add_bullet_point(doc, 'Opacity slider: Adjust tumor overlay transparency')
    
    add_heading_with_style(doc, '5.3. Statistics Panel', 2)
    
    add_styled_paragraph(doc,
        'Real-time statistics được cập nhật sau mỗi prediction:')
    
    stats_table = doc.add_table(rows=9, cols=2)
    stats_table.style = 'Light Grid Accent 1'
    
    stats = [
        ('Metric', 'Description'),
        ('Total Slices', 'Tổng số slices trong CT scan'),
        ('Scanned Slices', 'Số slices đã được xử lý'),
        ('Tumor Detected', 'Số slices có phát hiện khối u'),
        ('Total Tumor Pixels', 'Tổng số pixels được classify là tumor'),
        ('Tumor Volume (mm³)', 'Thể tích khối u ước tính'),
        ('Average Tumor Area', 'Diện tích trung bình trên mỗi slice'),
        ('Max Tumor Area', 'Slice có diện tích tumor lớn nhất'),
        ('Processing Time', 'Thời gian xử lý (ms/slice, total)')
    ]
    
    for i, (col1, col2) in enumerate(stats):
        row = stats_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '5.3.1. Volume Calculation', 3)
    
    add_code_block(doc, '''def calculate_tumor_volume(tumor_pixels, spacing):
    """
    Calculate tumor volume in mm³
    Args:
        tumor_pixels: Total number of tumor pixels across all slices
        spacing: Voxel spacing (x_mm, y_mm, z_mm)
    """
    pixel_area_mm2 = spacing[0] * spacing[1]  # Area per pixel
    slice_thickness_mm = spacing[2]           # Distance between slices
    
    volume_mm3 = tumor_pixels * pixel_area_mm2 * slice_thickness_mm
    volume_cm3 = volume_mm3 / 1000  # Convert to cm³
    
    return volume_mm3, volume_cm3''')
    
    add_heading_with_style(doc, '5.4. Model Information Card', 2)
    
    add_styled_paragraph(doc,
        'Glass card hiển thị thông tin về models đang sử dụng:')
    
    add_bullet_point(doc, 'Model names: unet_best_pancreas.keras, unet_best_tumor.keras')
    add_bullet_point(doc, 'Architecture: U-Net CNN')
    add_bullet_point(doc, 'Input sizes: 256×256 (pancreas), 128×128 (tumor)')
    add_bullet_point(doc, 'Performance metrics: Dice score, accuracy')
    add_bullet_point(doc, 'Context-aware: Enabled/Disabled status')
    
    add_heading_with_style(doc, '5.5. Action Buttons', 2)
    
    action_table = doc.add_table(rows=6, cols=3)
    action_table.style = 'Light Grid Accent 1'
    
    actions = [
        ('Button', 'Function', 'Icon'),
        ('Scan Current Slice', 'Process single slice', 'search'),
        ('Scan All Slices', 'Batch process with context', 'playlist_play'),
        ('Generate 3D Model', 'Create interactive 3D view', 'view_in_ar'),
        ('Reset Context', 'Clear prediction history', 'refresh'),
        ('Export Results', 'Save masks and statistics', 'save')
    ]
    
    for i, (col1, col2, col3) in enumerate(actions):
        row = action_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        row.cells[2].text = col3
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '5.6. Loading States & Feedback', 2)
    
    add_heading_with_style(doc, '5.6.1. Loading Indicators', 3)
    add_bullet_point(doc, 'Circular progress bar cho file upload')
    add_bullet_point(doc, 'Linear progress bar cho batch processing')
    add_bullet_point(doc, 'Skeleton loaders cho image preview')
    add_bullet_point(doc, 'Shimmer effects trên cards đang load')
    
    add_heading_with_style(doc, '5.6.2. User Feedback', 3)
    add_bullet_point(doc, 'Snackbars: Success (green), Error (red), Info (blue)')
    add_bullet_point(doc, 'Toast messages: Quick notifications')
    add_bullet_point(doc, 'Status text: "Processing slice X/Y..."')
    add_bullet_point(doc, 'Disable buttons during operations')
    add_bullet_point(doc, 'Confirmation dialogs cho destructive actions')
    
    # =================================================================
    # SECTION 6: 3D VISUALIZATION
    # =================================================================
    doc.add_page_break()
    add_heading_with_style(doc, '6. TRỰC QUAN HÓA 3D', 1)
    
    add_styled_paragraph(doc,
        'Module 3D visualization cho phép bác sĩ tương tác với CT scan trong không gian 3D, '
        'kết hợp volume rendering (toàn bộ cơ thể) với surface meshes (tụy và khối u).')
    
    add_heading_with_style(doc, '6.1. Marching Cubes Algorithm', 2)
    
    add_styled_paragraph(doc,
        'Thuật toán marching cubes chuyển đổi 3D volume data (binary masks) thành '
        'polygon meshes có thể render được.')
    
    add_heading_with_style(doc, '6.1.1. Algorithm Steps', 3)
    
    add_bullet_point(doc, '1. Chia volume thành các cube 2×2×2 voxels')
    add_bullet_point(doc, '2. Với mỗi cube, kiểm tra 8 đỉnh (trong/ngoài surface)')
    add_bullet_point(doc, '3. Tạo 8-bit index từ trạng thái 8 đỉnh')
    add_bullet_point(doc, '4. Lookup table → Cấu hình triangles (256 cases)')
    add_bullet_point(doc, '5. Interpolate vertex positions dọc cube edges')
    add_bullet_point(doc, '6. Generate vertices array (M×3) và faces array (K×3)')
    add_bullet_point(doc, '7. Calculate normal vectors cho lighting')
    add_bullet_point(doc, '8. Apply affine transformation (voxel → physical space)')
    
    add_code_block(doc, '''from skimage.measure import marching_cubes

# Generate mesh from 3D mask
vertices, faces, normals, values = marching_cubes(
    mask_3d, 
    level=0.5,
    spacing=spacing,  # (x_mm, y_mm, z_mm)
    step_size=1
)

# Vertices: Nx3 array of (x, y, z) coordinates in mm
# Faces: Mx3 array of triangle vertex indices
# Normals: Nx3 array of normal vectors for lighting''')
    
    add_heading_with_style(doc, '6.2. Mesh Simplification', 2)
    
    add_styled_paragraph(doc,
        'Raw marching cubes output thường có hàng triệu triangles, quá lớn để render '
        'hiệu quả trong browser. Mesh simplification giảm polygon count.')
    
    add_code_block(doc, '''import trimesh

mesh = trimesh.Trimesh(vertices=verts, faces=faces)

# Target: 10,000 faces (good balance quality/performance)
if len(mesh.faces) > 10000:
    mesh = mesh.simplify_quadric_decimation(10000)

# Export to GLB format
mesh.export('model.glb', file_type='glb')''')
    
    add_heading_with_style(doc, '6.3. Volume Rendering', 2)
    
    add_styled_paragraph(doc,
        'Volume rendering hiển thị toàn bộ CT scan với transparency, cho phép nhìn '
        'xuyên qua cấu trúc bên trong. Sử dụng ray marching algorithm.')
    
    add_heading_with_style(doc, '6.3.1. Ray Marching Process', 3)
    
    add_bullet_point(doc, '1. Cast ray từ camera qua mỗi pixel màn hình')
    add_bullet_point(doc, '2. Ray đi xuyên qua 3D texture (volume data)')
    add_bullet_point(doc, '3. Sample volume tại các bước đều (64-256 samples)')
    add_bullet_point(doc, '4. Mỗi sample: HU value → RGBA qua transfer function')
    add_bullet_point(doc, '5. Accumulate colors: Front-to-back alpha compositing')
    add_bullet_point(doc, '6. Early ray termination khi opacity > 0.95')
    add_bullet_point(doc, '7. Output: Final pixel color')
    
    add_code_block(doc, '''// Fragment shader (GLSL)
vec4 rayMarch(vec3 rayOrigin, vec3 rayDir) {
    vec4 color = vec4(0.0);
    float t = 0.0;
    
    for (int i = 0; i < 256; i++) {
        vec3 pos = rayOrigin + rayDir * t;
        
        // Sample volume
        float value = texture(volumeTexture, pos).r;
        
        // Transfer function: HU -> RGBA
        vec4 sample = transferFunction(value);
        
        // Alpha compositing
        color.rgb += (1.0 - color.a) * sample.a * sample.rgb;
        color.a += (1.0 - color.a) * sample.a;
        
        // Early termination
        if (color.a > 0.95) break;
        
        t += stepSize;
    }
    
    return color;
}''')
    
    add_heading_with_style(doc, '6.3.2. Transfer Function', 3)
    
    add_styled_paragraph(doc,
        'Transfer function map HU values → color và opacity:')
    
    tf_table = doc.add_table(rows=5, cols=3)
    tf_table.style = 'Light Grid Accent 1'
    
    transfer = [
        ('HU Range', 'Color', 'Opacity'),
        ('< -150 (Air)', 'Transparent', '0%'),
        ('-150 to 50 (Soft tissue)', 'Brown/Tan', '10-30%'),
        ('50 to 250 (Dense tissue)', 'Orange', '30-50%'),
        ('> 400 (Bone)', 'White', '50-80%')
    ]
    
    for i, (col1, col2, col3) in enumerate(transfer):
        row = tf_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        row.cells[2].text = col3
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '6.4. Three.js Integration', 2)
    
    add_styled_paragraph(doc,
        'Flutter WebView embed Three.js scene cho interactive 3D rendering:')
    
    add_code_block(doc, '''// Three.js scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

// Add lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);

// Load GLB models
const loader = new GLTFLoader();
loader.parse(glbData, '', (gltf) => {
    scene.add(gltf.scene);
});

// OrbitControls for interaction
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}''')
    
    add_heading_with_style(doc, '6.5. 3D Viewer Controls', 2)
    
    controls_table = doc.add_table(rows=9, cols=2)
    controls_table.style = 'Light Grid Accent 1'
    
    controls_data = [
        ('Control', 'Action'),
        ('Left Click + Drag', 'Rotate camera around model'),
        ('Right Click + Drag', 'Pan camera'),
        ('Mouse Wheel', 'Zoom in/out'),
        ('Double Click', 'Focus on clicked point'),
        ('Volume Opacity Slider', 'Adjust volume transparency (0-1)'),
        ('Toggle Volume', 'Show/hide volume rendering'),
        ('Toggle Meshes', 'Show/hide surface meshes'),
        ('Reset Camera', 'Return to default view')
    ]
    
    for i, (col1, col2) in enumerate(controls_data):
        row = controls_table.rows[i]
        row.cells[0].text = col1
        row.cells[1].text = col2
        if i == 0:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.bold = True
    
    doc.add_paragraph()
    
    add_heading_with_style(doc, '6.6. Performance Optimization', 2)
    
    add_bullet_point(doc, 'Downsample volume: 512³ → 256³ (8× reduction)')
    add_bullet_point(doc, 'Mesh simplification: ~100K → ~10K faces')
    add_bullet_point(doc, 'Level of Detail (LOD): Low-res khi zoom out')
    add_bullet_point(doc, 'Frustum culling: Không render objects ngoài view')
    add_bullet_point(doc, 'WebGL 2.0: 3D textures, efficient shaders')
    add_bullet_point(doc, 'Progressive loading: Meshes load trước, volume sau')
    add_bullet_point(doc, 'GPU memory management: Dispose unused textures')
    
    # Save
    doc.save(r"Research Paper\Full_System_Documentation_Vietnamese.docx")
    print(f"\n✓ Updated document with Part 2")
    print(f"  Added sections: 5 (UI/UX), 6 (3D Visualization)")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Creating Comprehensive System Documentation - Part 2")
    print("="*70)
    create_part2()
    print("="*70 + "\n")
