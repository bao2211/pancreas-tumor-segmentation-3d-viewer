"""
Create Vietnamese translation of 3D Viewer Implementation Documentation
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Create a new Document
document = Document()

# Set default font
style = document.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(11)

# ============================================================================
# TRANG BÌA
# ============================================================================
title = document.add_heading('Tài Liệu Triển Khai Trực Quan Hóa 3D', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = document.add_paragraph('Hệ Thống Render Volume 3D Tương Tác Cho Phát Hiện Khối U Tụy')
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.runs[0].font.size = Pt(14)
subtitle.runs[0].font.color.rgb = RGBColor(0, 102, 204)

document.add_paragraph()
document.add_paragraph()

# Project info
info = document.add_paragraph()
info.add_run('Dự Án: ').bold = True
info.add_run('Hệ Thống Phân Đoạn Tụy Đa Nền Tảng\n')
info.add_run('Thành Phần: ').bold = True
info.add_run('Trình Xem 3D Volume\n')
info.add_run('Ngày Triển Khai: ').bold = True
info.add_run('Tháng 1 năm 2026\n')
info.add_run('Trạng Thái: ').bold = True
info.add_run('Sẵn Sàng Đưa Vào Sử Dụng').font.color.rgb = RGBColor(0, 176, 80)
info.alignment = WD_ALIGN_PARAGRAPH.CENTER

document.add_page_break()

# ============================================================================
# MỤC LỤC
# ============================================================================
document.add_heading('Mục Lục', 1)
toc_items = [
    '1. Tổng Quan',
    '2. Kiến Trúc Kỹ Thuật',
    '3. Triển Khai Backend (Python)',
    '4. Triển Khai Frontend (Flutter)',
    '5. Luồng Dữ Liệu và Xử Lý',
    '6. Giao Diện Người Dùng và Điều Khiển',
    '7. Tối Ưu Hóa Hiệu Suất',
    '8. Cài Đặt và Thiết Lập',
    '9. Hướng Dẫn Sử Dụng',
    '10. Xử Lý Sự Cố',
    '11. Cải Tiến Tương Lai'
]
for item in toc_items:
    document.add_paragraph(item, style='List Number')

document.add_page_break()

# ============================================================================
# 1. TỔNG QUAN
# ============================================================================
document.add_heading('1. Tổng Quan', 1)

document.add_heading('Mục Đích', 2)
p = document.add_paragraph(
    'Tính năng trực quan hóa 3D cho phép render tương tác các volume tụy và khối u '
    'được trích xuất từ kết quả phân đoạn CT scan. Điều này cung cấp cho bác sĩ lâm sàng '
    'cái nhìn không gian toàn diện về các cấu trúc giải phẫu và phát hiện bệnh lý.'
)

document.add_heading('Tính Năng Chính', 2)
features = [
    'Render 3D tương tác thời gian thực sử dụng WebGL',
    'Hiển thị riêng biệt cho tụy (cyan) và khối u (đỏ) với điều khiển hiển thị độc lập',
    'Điều khiển cảm ứng và chuột: xoay, phóng to và di chuyển',
    'Tự động tạo mesh từ các mask phân đoạn',
    'Tối ưu hóa mesh đơn giản hóa cho hiệu suất web',
    'Định dạng glTF chuẩn công nghiệp để trao đổi mô hình 3D',
    'Thiết kế UI glass-morphism chuyên nghiệp'
]
for feature in features:
    document.add_paragraph(feature, style='List Bullet')

document.add_heading('Công Nghệ Sử Dụng', 2)
tech_table = document.add_table(rows=6, cols=2)
tech_table.style = 'Light Grid Accent 1'

headers = tech_table.rows[0].cells
headers[0].text = 'Công Nghệ'
headers[1].text = 'Mục Đích'

tech_data = [
    ('Thuật Toán Marching Cubes', 'Trích xuất bề mặt 3D từ các mask volume nhị phân'),
    ('Thư Viện scikit-image', 'Triển khai marching cubes'),
    ('Thư Viện Trimesh', 'Xử lý mesh, đơn giản hóa, và xuất glTF'),
    ('Flutter 3D Controller', 'Render 3D dựa trên WebGL trong Flutter'),
    ('Định Dạng glTF', 'Định dạng mô hình 3D chuẩn công nghiệp cho web')
]

for i, (tech, purpose) in enumerate(tech_data, start=1):
    row = tech_table.rows[i].cells
    row[0].text = tech
    row[1].text = purpose

document.add_page_break()

# ============================================================================
# 2. KIẾN TRÚC KỸ THUẬT
# ============================================================================
document.add_heading('2. Kiến Trúc Kỹ Thuật', 1)

document.add_heading('Các Thành Phần Hệ Thống', 2)

document.add_heading('Backend (Python Server)', 3)
backend_components = [
    'Lưu trữ mask 3D toàn cục: Tích lũy kết quả phân đoạn trong quá trình quét',
    'Triển khai marching cubes: Tạo các đỉnh và mặt của mesh',
    'Đơn giản hóa mesh: Giảm số lượng polygon sử dụng quadric decimation',
    'Xuất glTF: Chuyển đổi mesh sang định dạng tương thích web',
    'HTTP endpoint: /generate_3d_model để lấy mô hình'
]
for component in backend_components:
    document.add_paragraph(component, style='List Bullet')

document.add_heading('Frontend (Flutter Web)', 3)
frontend_components = [
    'Widget Volume3DViewer: Thành phần render 3D toàn màn hình',
    'Tích hợp Flutter3DViewer: Engine render WebGL',
    'Điều khiển tương tác: Xử lý sự kiện cảm ứng và chuột',
    'Chuyển đổi hiển thị: Hiện/ẩn từng cơ quan',
    'Trạng thái loading: Chỉ báo tiến trình trong quá trình tạo'
]
for component in frontend_components:
    document.add_paragraph(component, style='List Bullet')

document.add_heading('Giao Thức Giao Tiếp', 2)
p = document.add_paragraph()
p.add_run('Frontend và backend giao tiếp qua HTTP REST API. Mô hình 3D được tạo '
          'theo yêu cầu khi người dùng nhấp ').font.size = Pt(11)
p.add_run('"Xem 3D"').bold = True
p.add_run('. Server trả về glTF nhị phân được mã hóa base64, được giải mã và '
          'render trực tiếp trong trình duyệt mà không cần truy cập hệ thống file.').font.size = Pt(11)

document.add_page_break()

# ============================================================================
# 3. TRIỂN KHAI BACKEND
# ============================================================================
document.add_heading('3. Triển Khai Backend (Python)', 1)

document.add_heading('Thuật Toán Cốt Lõi: Marching Cubes', 2)
p = document.add_paragraph(
    'Thuật toán marching cubes là phương pháp cổ điển để trích xuất một mesh đa giác '
    'từ trường vô hướng 3D (trong trường hợp này là các mask phân đoạn nhị phân). '
    'Nó hoạt động bằng cách kiểm tra từng ô khối trong volume và tạo các tam giác '
    'dựa trên đỉnh nào nằm trong hoặc ngoài bề mặt.'
)

document.add_heading('Các Bước Thuật Toán', 3)
steps = [
    'Chia volume 3D thành lưới các ô khối (voxel)',
    'Với mỗi khối, xác định góc nào nằm trong bề mặt (giá trị mask = 1)',
    'Sử dụng bảng tra cứu để xác định cấu hình tam giác (256 trường hợp có thể)',
    'Tạo các đỉnh tam giác bằng cách nội suy giữa các góc khối',
    'Kết hợp tất cả các tam giác để tạo thành mesh bề mặt liên tục'
]
for i, step in enumerate(steps, start=1):
    document.add_paragraph(f'{i}. {step}', style='List Number')

document.add_heading('Thuộc Tính Mesh', 2)
mesh_table = document.add_table(rows=3, cols=3)
mesh_table.style = 'Light Grid Accent 1'

headers = mesh_table.rows[0].cells
headers[0].text = 'Loại Mesh'
headers[1].text = 'Màu (RGBA)'
headers[2].text = 'Số Mặt Sau Đơn Giản Hóa'

row1 = mesh_table.rows[1].cells
row1[0].text = 'Tụy'
row1[1].text = 'Cyan (0, 255, 255, 150)'
row1[2].text = '10,000 mặt'

row2 = mesh_table.rows[2].cells
row2[0].text = 'Khối U'
row2[1].text = 'Đỏ (255, 0, 0, 220)'
row2[2].text = '5,000 mặt'

document.add_heading('Các Hàm Python Chính', 2)

document.add_heading('generate_3d_mesh_from_masks()', 3)
p = document.add_paragraph()
p.add_run('Mục Đích: ').bold = True
p.add_run('Trích xuất các mesh bề mặt 3D từ các mask nhị phân tích lũy\n\n')
p.add_run('Tham Số:\n').bold = True
params = [
    'volume_masks: Dictionary chứa mảng numpy 3D "pancreas" và "tumor"',
    'spacing: Tuple của (x, y, z) khoảng cách voxel tính bằng milimét (mặc định: 1.0, 1.0, 1.0)'
]
for param in params:
    p.add_run(f'  • {param}\n')
p.add_run('\nTrả Về: ').bold = True
p.add_run('Dữ liệu glTF nhị phân được mã hóa base64')

document.add_heading('Đơn Giản Hóa Mesh', 3)
p = document.add_paragraph(
    'Để đảm bảo hiệu suất web mượt mà, các mesh thô (thường 50K-200K mặt) được đơn giản hóa '
    'sử dụng quadric decimation. Thuật toán này bảo toàn hình dạng mesh trong khi giảm số lượng '
    'polygon, duy trì chất lượng hình ảnh với chi phí tính toán thấp hơn nhiều.'
)

document.add_heading('Xuất glTF', 3)
p = document.add_paragraph(
    'glTF (GL Transmission Format) là định dạng 3D ưu tiên cho ứng dụng web. '
    'Nó hỗ trợ nhiều mesh, vật liệu và mã hóa nhị phân hiệu quả. Triển khai '
    'sử dụng thư viện Trimesh để kết hợp mesh tụy và khối u thành một scene glTF '
    'với vật liệu và màu sắc phù hợp.'
)

document.add_page_break()

# ============================================================================
# 4. TRIỂN KHAI FRONTEND
# ============================================================================
document.add_heading('4. Triển Khai Frontend (Flutter)', 1)

document.add_heading('Widget Volume3DViewer', 2)
p = document.add_paragraph(
    'Volume3DViewer là widget Flutter tùy chỉnh cung cấp trải nghiệm trực quan hóa '
    '3D toàn màn hình. Nó tích hợp package flutter_3d_controller cho render WebGL '
    'và thêm các điều khiển UI tùy chỉnh để tương tác.'
)

document.add_heading('Tính Năng Widget', 3)
features = [
    'Chế độ xem toàn màn hình đắm chìm',
    'Nền đen để tối ưu hóa trực quan hóa 3D',
    'Bảng điều khiển glass-morphism nổi',
    'Chuyển đổi hiển thị thời gian thực với biểu tượng mã màu',
    'Nút đặt lại góc nhìn để quay về vị trí camera mặc định',
    'Trạng thái loading với chỉ báo tiến trình tròn',
    'Bố cục responsive thích ứng với kích thước màn hình'
]
for feature in features:
    document.add_paragraph(feature, style='List Bullet')

document.add_heading('Điều Khiển Tương Tác', 2)
controls_table = document.add_table(rows=6, cols=2)
controls_table.style = 'Light Grid Accent 1'

headers = controls_table.rows[0].cells
headers[0].text = 'Cử Chỉ/Đầu Vào'
headers[1].text = 'Hành Động'

controls = [
    ('Kéo (Chuột/Cảm Ứng)', 'Xoay mô hình quanh tâm'),
    ('Pinch / Bánh Xe Cuộn', 'Phóng to và thu nhỏ'),
    ('Kéo Hai Ngón', 'Di chuyển vị trí camera'),
    ('Chuyển Đổi Tụy', 'Hiện/ẩn mesh tụy'),
    ('Chuyển Đổi Khối U', 'Hiện/ẩn mesh khối u')
]

for i, (gesture, action) in enumerate(controls, start=1):
    row = controls_table.rows[i].cells
    row[0].text = gesture
    row[1].text = action

document.add_heading('Tích Hợp NiiService', 2)
p = document.add_paragraph()
p.add_run('Class NiiService xử lý giao tiếp với backend Python. Phương thức ').font.size = Pt(11)
p.add_run('generate3DModel()').font.name = 'Consolas'
p.add_run(' gửi POST request đến endpoint /generate_3d_model và nhận '
          'dữ liệu glTF được mã hóa base64. Phương thức này bao gồm xử lý lỗi thích hợp, '
          'quản lý timeout (120 giây), và cập nhật trạng thái loading.').font.size = Pt(11)

document.add_page_break()

# ============================================================================
# 5. LUỒNG DỮ LIỆU VÀ XỬ LÝ
# ============================================================================
document.add_heading('5. Luồng Dữ Liệu và Xử Lý', 1)

document.add_heading('Quy Trình Hoàn Chỉnh', 2)

workflow_steps = [
    ('Tải File Lên', 'Người dùng tải file NIfTI (.nii hoặc .nii.gz) chứa volume CT scan'),
    ('Tải Volume', 'Backend tải và xác thực file NIfTI, trích xuất metadata'),
    ('Xử Lý Slice', 'Mỗi slice được xử lý qua các mô hình U-Net để phân đoạn'),
    ('Tích Lũy Mask', 'Các mask tụy và khối u được tích lũy vào mảng 3D (256×256×N)'),
    ('Hoàn Thành Quét', 'Volume đầy đủ được xử lý, thống kê được tính toán'),
    ('Yêu Cầu Mô Hình 3D', 'Người dùng nhấp nút "Xem 3D", Flutter gửi request'),
    ('Marching Cubes', 'Server chạy marching cubes trên các mask tích lũy'),
    ('Đơn Giản Hóa Mesh', 'Các mesh được đơn giản hóa đến số mặt mục tiêu'),
    ('Tạo glTF', 'Scene kết hợp được xuất dưới dạng glTF nhị phân'),
    ('Truyền Dữ Liệu', 'glTF được mã hóa base64 gửi đến Flutter qua HTTP'),
    ('Render 3D', 'Flutter giải mã và render mô hình sử dụng WebGL'),
    ('Tương Tác Người Dùng', 'Người dùng có thể xoay, phóng to, chuyển đổi hiển thị')
]

for i, (stage, description) in enumerate(workflow_steps, start=1):
    p = document.add_paragraph()
    p.add_run(f'{i}. {stage}: ').bold = True
    p.add_run(description)

document.add_heading('Logic Tích Lũy Mask', 2)
p = document.add_paragraph(
    'Trong quá trình quét, mỗi slice tạo ra hai mask nhị phân (tụy và khối u). '
    'Các mask 2D này được xếp chồng dọc theo trục Z để tạo volume 3D. Việc tích lũy '
    'diễn ra tự động trong quá trình quét, đảm bảo tất cả dữ liệu slice có sẵn '
    'để tạo mesh 3D mà không cần xử lý bổ sung.'
)

accumulation_table = document.add_table(rows=4, cols=2)
accumulation_table.style = 'Light List Accent 1'

headers = accumulation_table.rows[0].cells
headers[0].text = 'Thuộc Tính'
headers[1].text = 'Giá Trị'

acc_data = [
    ('Kích thước mask', '256 × 256 × N (N = số lượng slice)'),
    ('Kiểu dữ liệu', 'uint8 (0 hoặc 1)'),
    ('Bộ nhớ mỗi volume', '~2-10 MB tùy thuộc vào số lượng slice')
]

for i, (prop, val) in enumerate(acc_data, start=1):
    row = accumulation_table.rows[i].cells
    row[0].text = prop
    row[1].text = val

document.add_heading('Cách Hoạt Động của CT Volume Rendering', 2)

document.add_heading('Cấu Trúc Dữ Liệu CT Scan', 3)
p = document.add_paragraph(
    'CT scan tạo ra một volume 3D gồm nhiều lát cắt ngang (slices). Mỗi slice là một '
    'hình ảnh 2D thể hiện mặt cắt ngang của cơ thể bệnh nhân. Khi xếp chồng các slice '
    'này theo đúng thứ tự, chúng tạo thành một khối dữ liệu 3D (volume) hoàn chỉnh.'
)

ct_structure = [
    'Volume gốc: Mảng 3D với kích thước (Cao × Rộng × Số Slice)',
    'Ví dụ: 512 × 512 × 200 = một volume có 200 lát cắt, mỗi slice 512×512 pixels',
    'Mỗi pixel (voxel trong 3D) chứa giá trị cường độ Hounsfield Unit (HU)',
    'Khoảng cách voxel (spacing): Khoảng cách vật lý giữa các voxel trong không gian thực (mm)',
    'Ma trận affine: Chuyển đổi từ tọa độ voxel sang tọa độ không gian thế giới (world coordinates)'
]
for item in ct_structure:
    document.add_paragraph(item, style='List Bullet')

document.add_heading('Pipeline Xử Lý CT Volume', 3)
p = document.add_paragraph(
    'Quá trình từ dữ liệu CT thô đến mô hình 3D tương tác trải qua nhiều giai đoạn:'
)

pipeline_table = document.add_table(rows=8, cols=3)
pipeline_table.style = 'Medium Grid 3 Accent 1'

headers = pipeline_table.rows[0].cells
headers[0].text = 'Giai Đoạn'
headers[1].text = 'Đầu Vào'
headers[2].text = 'Đầu Ra'

pipeline_data = [
    ('1. Load NIfTI', 'File .nii/.nii.gz', 'Volume 3D array + metadata'),
    ('2. HU Windowing', 'Raw HU values', 'Normalized 0-255 grayscale'),
    ('3. Slice Extraction', 'Volume 3D', 'Individual 2D slices'),
    ('4. U-Net Inference', '2D slice image', 'Binary mask (pancreas/tumor)'),
    ('5. Mask Accumulation', 'Multiple 2D masks', '3D mask volume'),
    ('6. Marching Cubes', '3D mask volume', '3D mesh (vertices + faces)'),
    ('7. Mesh Processing', 'Raw mesh', 'Simplified + colored mesh')
]

for i, (stage, input_data, output) in enumerate(pipeline_data, start=1):
    row = pipeline_table.rows[i].cells
    row[0].text = stage
    row[1].text = input_data
    row[2].text = output

document.add_heading('Chi Tiết Từng Bước', 3)

document.add_heading('Bước 1-2: Load và Chuẩn Hóa', 4)
p = document.add_paragraph()
p.add_run('File NIfTI chứa:\n').bold = True
load_details = [
    'Volume data: Mảng 3D với giá trị HU (-1000 đến +3000)',
    'Affine matrix: Ma trận 4×4 để chuyển đổi tọa độ',
    'Spacing: Khoảng cách vật lý (vd: 0.7mm × 0.7mm × 2.5mm)',
    'Metadata: Thông tin bệnh nhân, thiết bị, tham số chụp'
]
for detail in load_details:
    p.add_run(f'  • {detail}\n')

p.add_run('\nHU Windowing áp dụng:\n').bold = True
p.add_run('  • Chọn window phù hợp: -150 HU đến 250 HU (soft tissue)\n')
p.add_run('  • Clip giá trị ngoài range\n')
p.add_run('  • Normalize về 0-255 để hiển thị và xử lý\n')
p.add_run('  • Công thức: pixel = (HU - min) / (max - min) × 255')

document.add_heading('Bước 3-4: Phân Đoạn Từng Slice', 4)
p = document.add_paragraph(
    'Mỗi slice 2D được xử lý độc lập qua hai mô hình U-Net:\n\n'
)
p.add_run('Mô Hình 1 - Phân Đoạn Tụy:\n').bold = True
pancreas_process = [
    'Input: Slice 256×256×1 (grayscale)',
    'U-Net encoder: Trích xuất features qua 4 levels',
    'U-Net decoder: Tái tạo mask qua upsampling + skip connections',
    'Output: Binary mask 256×256 (0 = nền, 1 = tụy)',
    'Post-processing: Morphological operations để làm mượt'
]
for item in pancreas_process:
    p.add_run(f'  • {item}\n')

p.add_run('\nMô Hình 2 - Phát Hiện Khối U:\n').bold = True
tumor_process = [
    'Input: Vùng ROI (region of interest) từ pancreas mask, resize 128×128',
    'U-Net tương tự nhưng nhỏ hơn (ít parameters)',
    'Output: Binary mask khối u trong vùng tụy',
    'Context-aware refinement: Sử dụng thông tin từ 3 slices liền kề',
    'Map mask trở lại tọa độ gốc của volume'
]
for item in tumor_process:
    p.add_run(f'  • {item}\n')

document.add_heading('Bước 5: Tích Lũy Mask 3D', 4)
p = document.add_paragraph(
    'Trong quá trình quét, masks 2D được xếp chồng để tạo volume 3D:\n'
)

accumulation_code = '''# Khởi tạo mảng 3D rỗng
pancreas_volume = np.zeros((256, 256, num_slices), dtype=np.uint8)
tumor_volume = np.zeros((256, 256, num_slices), dtype=np.uint8)

# Với mỗi slice được xử lý
for z in range(num_slices):
    slice_data = ct_volume[:, :, z]
    
    # Phân đoạn
    pancreas_mask = pancreas_model.predict(slice_data)  # 256×256
    tumor_mask = tumor_model.predict(slice_data)        # 256×256
    
    # Tích lũy vào volume 3D
    pancreas_volume[:, :, z] = pancreas_mask
    tumor_volume[:, :, z] = tumor_mask

# Kết quả: Hai volumes 3D hoàn chỉnh'''

code_para = document.add_paragraph()
run = code_para.add_run(accumulation_code)
run.font.name = 'Consolas'
run.font.size = Pt(9)

document.add_heading('Bước 6: Marching Cubes - Trích Xuất Bề Mặt', 4)
p = document.add_paragraph(
    'Marching Cubes chuyển đổi volume nhị phân thành mesh 3D:\n\n'
)

p.add_run('Nguyên Lý:\n').bold = True
marching_cubes_principle = [
    'Chia volume thành các ô khối 2×2×2 (8 đỉnh)',
    'Với mỗi khối, kiểm tra 8 đỉnh: trong (1) hay ngoài (0) bề mặt',
    'Tạo ra 2⁸ = 256 cấu hình có thể',
    'Tra bảng lookup để biết tam giác nào cần tạo',
    'Nội suy vị trí đỉnh tam giác chính xác',
    'Kết nối các tam giác tạo mesh liên tục'
]
for item in marching_cubes_principle:
    p.add_run(f'  • {item}\n')

p.add_run('\nInput và Output:\n').bold = True
p.add_run('  • Input: pancreas_volume (256×256×N) với threshold = 0.5\n')
p.add_run('  • Output vertices: Mảng Mx3 (tọa độ x,y,z của M đỉnh)\n')
p.add_run('  • Output faces: Mảng Kx3 (chỉ số 3 đỉnh tạo K tam giác)\n')
p.add_run('  • Output normals: Mảng Mx3 (vector pháp tuyến tại mỗi đỉnh)\n\n')

p.add_run('Áp Dụng Spacing:\n').bold = True
p.add_run('  • Vertices được nhân với spacing để có tọa độ vật lý chính xác\n')
p.add_run('  • Ví dụ: spacing (0.7, 0.7, 2.5) mm\n')
p.add_run('  • vertex_physical = vertex_voxel × spacing\n')
p.add_run('  • Đảm bảo tỷ lệ chính xác giữa các trục')

document.add_heading('Bước 7: Xử Lý và Tối Ưu Mesh', 4)

mesh_processing_table = document.add_table(rows=6, cols=2)
mesh_processing_table.style = 'Light Grid Accent 1'

headers = mesh_processing_table.rows[0].cells
headers[0].text = 'Thao Tác'
headers[1].text = 'Mục Đích'

mesh_ops = [
    ('Simplification', 'Giảm từ 50K-200K faces xuống 10K/5K'),
    ('Smoothing', 'Làm mượt bề mặt, giảm răng cưa'),
    ('Coloring', 'Gán màu và độ trong suốt (cyan/red)'),
    ('Normal Calculation', 'Tính vector pháp tuyến cho lighting'),
    ('glTF Export', 'Đóng gói thành format chuẩn web')
]

for i, (operation, purpose) in enumerate(mesh_ops, start=1):
    row = mesh_processing_table.rows[i].cells
    row[0].text = operation
    row[1].text = purpose

document.add_heading('Ma Trận Affine và Hệ Tọa Độ', 3)
p = document.add_paragraph(
    'Ma trận affine 4×4 trong file NIfTI định nghĩa chuyển đổi từ tọa độ voxel sang '
    'tọa độ không gian thế giới (patient coordinates):\n'
)

affine_explanation = '''# Ma trận affine 4×4
# [R11 R12 R13 Tx]   [i]   [x]
# [R21 R22 R23 Ty] × [j] = [y]
# [R31 R32 R33 Tz]   [k]   [z]
# [ 0   0   0   1]   [1]   [1]

# Trong đó:
# (i,j,k) = tọa độ voxel (chỉ số trong mảng)
# (x,y,z) = tọa độ không gian thế giới (mm)
# R = ma trận rotation + scaling (3×3)
# T = vector translation (Tx, Ty, Tz)

# Ví dụ với spacing (0.7, 0.7, 2.5):
# Affine ≈ [[0.7  0    0   origin_x]
#           [0    0.7  0   origin_y]
#           [0    0    2.5 origin_z]
#           [0    0    0   1        ]]'''

affine_para = document.add_paragraph()
run = affine_para.add_run(affine_explanation)
run.font.name = 'Consolas'
run.font.size = Pt(9)

document.add_heading('Từ Volume 3D đến WebGL Rendering', 3)
p = document.add_paragraph(
    'Sau khi có mesh 3D, quá trình render trong trình duyệt:\n\n'
)

p.add_run('1. glTF Scene Construction:\n').bold = True
p.add_run('  • Mesh được đóng gói vào glTF binary format\n')
p.add_run('  • Bao gồm: vertices, faces, normals, colors, materials\n')
p.add_run('  • Tối ưu cho truyền tải qua mạng (compressed)\n\n')

p.add_run('2. Base64 Encoding:\n').bold = True
p.add_run('  • glTF binary được mã hóa base64\n')
p.add_run('  • Có thể truyền trực tiếp qua JSON response\n')
p.add_run('  • Không cần lưu file tạm trên server hay client\n\n')

p.add_run('3. Flutter 3D Controller:\n').bold = True
p.add_run('  • Nhận base64 data từ HTTP response\n')
p.add_run('  • Decode và parse glTF structure\n')
p.add_run('  • Tạo WebGL buffers (vertex, index, normal)\n')
p.add_run('  • Setup shaders cho rendering\n\n')

p.add_run('4. WebGL Rendering:\n').bold = True
webgl_details = [
    'Camera setup: Perspective projection với FOV 45°',
    'Lighting: Ambient + directional light cho depth perception',
    'Blending: Alpha blending cho transparency',
    'Culling: Back-face culling để tăng performance',
    'Interactive: Event handlers cho touch/mouse input',
    'Frame loop: 60 FPS continuous rendering'
]
for detail in webgl_details:
    p.add_run(f'  • {detail}\n')

document.add_heading('Metrics và Thống Kê', 3)

metrics_table = document.add_table(rows=7, cols=2)
metrics_table.style = 'Light List Accent 1'

headers = metrics_table.rows[0].cells
headers[0].text = 'Metric'
headers[1].text = 'Giá Trị Điển Hình'

metrics_data = [
    ('CT Volume Size', '512×512×200 = 52 MB (raw)'),
    ('Mask Volume Size', '256×256×200 = 13 MB'),
    ('Raw Mesh Faces', '50,000-200,000 faces'),
    ('Simplified Mesh', '10,000 (pancreas) + 5,000 (tumor)'),
    ('glTF File Size', '1-5 MB (compressed)'),
    ('WebGL Memory', '~50-100 MB (textures + buffers)')
]

for i, (metric, value) in enumerate(metrics_data, start=1):
    row = metrics_table.rows[i].cells
    row[0].text = metric
    row[1].text = value

document.add_page_break()

# ============================================================================
# 6. GIAO DIỆN NGƯỜI DÙNG VÀ ĐIỀU KHIỂN
# ============================================================================
document.add_heading('6. Giao Diện Người Dùng và Điều Khiển', 1)

document.add_heading('Tích Hợp Màn Hình Chính', 2)
p = document.add_paragraph()
p.add_run('Nút "Xem 3D" xuất hiện trên màn hình quét chính sau khi quét đầy đủ hoàn tất. '
          'Nó được tạo kiểu với màu teal accent (#06B6D4) của ứng dụng và có biểu tượng '
          'hình khối. Khi nhấp, hộp thoại loading xuất hiện trong khi mô hình 3D được tạo.')

document.add_heading('Bố Cục Màn Hình 3D Viewer', 2)

layout_components = [
    ('Nền', 'Đen đặc (Colors.black) để tương phản xem 3D tối ưu'),
    ('Mô Hình 3D', 'Căn giữa, lấp đầy phần lớn không gian màn hình'),
    ('Bảng Điều Khiển', 'Bảng glass-morphism nổi ở góc dưới phải'),
    ('Hướng Dẫn', 'Văn bản trợ giúp ngắn gọn ở đầu bảng điều khiển'),
    ('Công Tắc Hiển Thị', 'Công tắc chuyển đổi với biểu tượng và nhãn mã màu'),
    ('Nút Hành Động', 'Nút Đặt Lại Góc Nhìn và Hoàn Tất ở cuối bảng điều khiển')
]

for component, description in layout_components:
    p = document.add_paragraph()
    p.add_run(f'{component}: ').bold = True
    p.add_run(description)

document.add_heading('Các Yếu Tố Thiết Kế Trực Quan', 2)

design_table = document.add_table(rows=5, cols=2)
design_table.style = 'Light Grid Accent 1'

headers = design_table.rows[0].cells
headers[0].text = 'Yếu Tố'
headers[1].text = 'Chi Tiết Phong Cách'

design_data = [
    ('Nền Bảng Điều Khiển', 'Hiệu ứng kính: trắng với độ mờ 10%, làm mờ 16px'),
    ('Viền Bảng', 'Trắng 1px với độ mờ 30%'),
    ('Biểu Tượng Tụy', 'Hình tròn cyan (#06B6D4) khớp với màu mesh'),
    ('Biểu Tượng Khối U', 'Hình tròn đỏ (#EF4444) khớp với màu mesh')
]

for i, (element, style) in enumerate(design_data, start=1):
    row = design_table.rows[i].cells
    row[0].text = element
    row[1].text = style

document.add_heading('Hành Vi Responsive', 2)
p = document.add_paragraph(
    '3D viewer thích ứng với các kích thước màn hình khác nhau. Trên màn hình nhỏ hơn, '
    'bảng điều khiển giảm kích thước và văn bản có thể điều chỉnh. Mô hình 3D luôn duy trì '
    'tỷ lệ khung hình và lấp đầy không gian khả dụng trong khi để chỗ cho các điều khiển.'
)

document.add_page_break()

# ============================================================================
# 7. TỐI ƯU HÓA HIỆU SUẤT
# ============================================================================
document.add_heading('7. Tối Ưu Hóa Hiệu Suất', 1)

document.add_heading('Phân Tích Thời Gian Xử Lý', 2)

time_table = document.add_table(rows=6, cols=3)
time_table.style = 'Medium Grid 3 Accent 1'

headers = time_table.rows[0].cells
headers[0].text = 'Thao Tác'
headers[1].text = 'Khoảng Thời Gian'
headers[2].text = 'Yếu Tố'

time_data = [
    ('Marching Cubes (Tụy)', '2-5 giây', 'Số slice, thể tích mô'),
    ('Marching Cubes (Khối U)', '0.5-2 giây', 'Kích thước u, số lần phát hiện'),
    ('Đơn Giản Hóa Mesh', '1-3 giây', 'Số mặt gốc, mặt mục tiêu'),
    ('Xuất glTF', '0.5-1 giây', 'Độ phức tạp mesh'),
    ('Tổng Thời Gian Tạo', '5-15 giây', 'Các yếu tố kết hợp')
]

for i, (operation, time, factors) in enumerate(time_data, start=1):
    row = time_table.rows[i].cells
    row[0].text = operation
    row[1].text = time
    row[2].text = factors

document.add_heading('Tối Ưu Hóa Bộ Nhớ', 2)

memory_strategies = [
    'Lazy Loading: Mô hình 3D chỉ được tạo khi có yêu cầu',
    'Dọn Dẹp Tự Động: Mask được đặt lại khi tải volume mới',
    'Mã Hóa Hiệu Quả: Truyền base64 tránh file tạm',
    'Đơn Giản Hóa Mesh: Giảm dấu chân bộ nhớ 80-90%',
    'Scene Đơn: glTF kết hợp loại bỏ tài nguyên trùng lặp'
]

for strategy in memory_strategies:
    document.add_paragraph(strategy, style='List Bullet')

document.add_heading('Tối Ưu Hóa Truyền Mạng', 2)
p = document.add_paragraph(
    'Định dạng glTF nhị phân được nén cao. Kết hợp với mã hóa base64, kích thước '
    'mô hình điển hình dao động từ 1-5 MB. Truyền HTTP sử dụng mã hóa chunked để '
    'stream các response lớn hiệu quả. Timeout được đặt 120 giây để phù hợp với '
    'kết nối chậm hơn.'
)

document.add_heading('Hiệu Suất Trình Duyệt', 2)
browser_table = document.add_table(rows=5, cols=2)
browser_table.style = 'Light List Accent 1'

headers = browser_table.rows[0].cells
headers[0].text = 'Trình Duyệt'
headers[1].text = 'Ghi Chú Hiệu Suất'

browser_data = [
    ('Chrome (Khuyến Nghị)', 'Hỗ trợ WebGL tuyệt vời, render mượt mà 60fps'),
    ('Edge', 'Cùng engine Chromium như Chrome, hiệu suất tương đương'),
    ('Firefox', 'Hỗ trợ tốt nhưng có thể hơi lag với mesh phức tạp'),
    ('Safari', 'Hiệu suất WebGL thay đổi tùy phiên bản')
]

for i, (browser, notes) in enumerate(browser_data, start=1):
    row = browser_table.rows[i].cells
    row[0].text = browser
    row[1].text = notes

document.add_page_break()

# ============================================================================
# 8. CÀI ĐẶT VÀ THIẾT LẬP
# ============================================================================
document.add_heading('8. Cài Đặt và Thiết Lập', 1)

document.add_heading('Dependencies Backend', 2)

p = document.add_paragraph()
p.add_run('File: ').bold = True
p.add_run('pancreas_segmentation_app/requirements_nii.txt\n\n')
p.add_run('Các package cần thiết:\n').bold = True

backend_deps = [
    'scikit-image>=0.21.0  # Thuật toán marching cubes',
    'trimesh>=3.23.0       # Xử lý mesh và xuất glTF',
    'numpy>=1.23.0         # Các thao tác số',
    'nibabel>=5.0.0        # Xử lý file NIfTI',
    'tensorflow>=2.10.0    # Mô hình học sâu',
    'opencv-python>=4.7.0  # Xử lý hình ảnh'
]

for dep in backend_deps:
    p.add_run(f'  • {dep}\n')

document.add_heading('Lệnh Cài Đặt', 3)
p = document.add_paragraph()
run = p.add_run('cd pancreas_segmentation_app\n')
run.font.name = 'Consolas'
run.font.size = Pt(10)
run = p.add_run('pip install -r requirements_nii.txt')
run.font.name = 'Consolas'
run.font.size = Pt(10)

document.add_heading('Dependencies Frontend', 2)

p = document.add_paragraph()
p.add_run('File: ').bold = True
p.add_run('pancreas_segmentation_app/pubspec.yaml\n\n')
p.add_run('Các package cần thiết:\n').bold = True

frontend_deps = [
    'flutter: sdk: flutter  # Flutter framework',
    'provider: ^6.1.1       # Quản lý state',
    'http: ^1.6.0           # HTTP requests',
    'file_picker: ^10.0.0   # Chọn file',
    'flutter_3d_controller: ^1.3.1  # Render mô hình 3D'
]

for dep in frontend_deps:
    p.add_run(f'  • {dep}\n')

document.add_heading('Lệnh Cài Đặt', 3)
p = document.add_paragraph()
run = p.add_run('cd pancreas_segmentation_app\n')
run.font.name = 'Consolas'
run.font.size = Pt(10)
run = p.add_run('flutter pub get')
run.font.name = 'Consolas'
run.font.size = Pt(10)

document.add_heading('Yêu Cầu Hệ Thống', 2)

req_table = document.add_table(rows=4, cols=2)
req_table.style = 'Light Grid Accent 1'

headers = req_table.rows[0].cells
headers[0].text = 'Thành Phần'
headers[1].text = 'Yêu Cầu Tối Thiểu'

reqs = [
    ('CPU', 'Intel i5 hoặc tương đương (4 cores)'),
    ('RAM', '8 GB (khuyến nghị 16 GB)'),
    ('Trình Duyệt', 'Chrome/Edge với hỗ trợ WebGL 2.0')
]

for i, (component, requirement) in enumerate(reqs, start=1):
    row = req_table.rows[i].cells
    row[0].text = component
    row[1].text = requirement

document.add_page_break()

# ============================================================================
# 9. HƯỚNG DẪN SỬ DỤNG
# ============================================================================
document.add_heading('9. Hướng Dẫn Sử Dụng', 1)

document.add_heading('Hướng Dẫn Từng Bước', 2)

usage_steps = [
    ('Khởi Động Backend Server', 
     'Chạy: python nii_inference_server.py\nServer khởi động tại http://localhost:8765'),
    
    ('Khởi Chạy Flutter App', 
     'Chạy: flutter run -d chrome\nApp mở trong trình duyệt Chrome'),
    
    ('Tải File NIfTI Lên', 
     'Nhấp nút "Upload NIfTI File"\nChọn file .nii hoặc .nii.gz\nĐợi file tải xong'),
    
    ('Chạy Quét Đầy Đủ', 
     'Nhấp nút "Start Full Scan"\nĐợi tất cả slice được xử lý\n'
     'Thanh tiến trình hiển thị trạng thái hoàn thành'),
    
    ('Xem Kết Quả 2D', 
     'Xem lại kết quả từng slice\nKiểm tra chất lượng phân đoạn\nĐiều hướng bằng slider'),
    
    ('Tạo Mô Hình 3D', 
     'Nhấp nút "View in 3D" (xuất hiện sau khi quét)\nĐợi tạo mô hình (5-15 giây)\n'
     'Hộp thoại loading hiển thị tiến trình'),
    
    ('Tương Tác với Mô Hình 3D', 
     'Kéo để xoay mô hình\nPinch/cuộn để phóng to\nHai ngón để di chuyển\n'
     'Chuyển đổi hiển thị tụy/khối u'),
    
    ('Đặt Lại và Đóng', 
     'Nhấp "Reset View" để quay về vị trí mặc định\nNhấp "Done" để đóng viewer')
]

for i, (title, instructions) in enumerate(usage_steps, start=1):
    document.add_heading(f'{i}. {title}', 3)
    for line in instructions.split('\n'):
        document.add_paragraph(line, style='List Bullet')

document.add_heading('Mẹo Để Có Kết Quả Tốt Nhất', 2)

tips = [
    'Đảm bảo quét đầy đủ hoàn thành trước khi yêu cầu xem 3D',
    'Sử dụng trình duyệt Chrome để có hiệu suất WebGL tốt nhất',
    'Bật tăng tốc phần cứng trong cài đặt trình duyệt',
    'Với volume lớn (>300 slice), mong đợi thời gian tạo lâu hơn',
    'Tắt một mesh để tập trung vào cơ quan khác',
    'Đặt lại góc nhìn nếu camera bị lệch trong quá trình tương tác'
]

for tip in tips:
    p = document.add_paragraph(tip, style='List Bullet')
    p.runs[0].font.color.rgb = RGBColor(0, 102, 204)

document.add_page_break()

# ============================================================================
# 10. XỬ LÝ SỰ CỐ
# ============================================================================
document.add_heading('10. Xử Lý Sự Cố', 1)

issues = [
    {
        'problem': 'Lỗi "Failed to generate 3D model"',
        'causes': [
            'Không có dữ liệu quét',
            'Dependencies backend chưa cài đặt',
            'Timeout kết nối server'
        ],
        'solutions': [
            'Đảm bảo quét đầy đủ hoàn thành trước khi yêu cầu xem 3D',
            'Xác minh scikit-image và trimesh đã được cài đặt',
            'Kiểm tra log server để biết thông báo lỗi chi tiết',
            'Tăng timeout trong NiiService nếu cần'
        ]
    },
    {
        'problem': '3D Viewer Hiển Thị Màn Hình Đen',
        'causes': [
            'WebGL không được hỗ trợ trong trình duyệt',
            'Tăng tốc phần cứng bị tắt',
            'Dữ liệu glTF không hợp lệ hoặc bị lỗi'
        ],
        'solutions': [
            'Sử dụng trình duyệt Chrome hoặc Edge',
            'Bật tăng tốc phần cứng trong cài đặt trình duyệt',
            'Kiểm tra console trình duyệt để biết lỗi WebGL',
            'Thử tạo lại mô hình 3D'
        ]
    },
    {
        'problem': 'Mô Hình Mất Quá Lâu Để Tạo',
        'causes': [
            'Số lượng slice lớn (>400)',
            'Số lần phát hiện khối u cao',
            'Hạn chế hiệu suất CPU'
        ],
        'solutions': [
            'Kiên nhẫn - việc tạo có thể mất 15-30 giây cho volume lớn',
            'Cân nhắc sử dụng máy tính mạnh hơn',
            'Kiểm tra xem có tác vụ tốn CPU khác đang chạy không',
            'Xác minh đơn giản hóa mesh đang hoạt động đúng'
        ]
    },
    {
        'problem': 'Mesh Xuất Hiện Biến Dạng Hoặc Không Chính Xác',
        'causes': [
            'Chất lượng phân đoạn kém',
            'Dữ liệu quét không đầy đủ',
            'Khoảng cách voxel không chính xác'
        ],
        'solutions': [
            'Xem lại kết quả slice 2D để xác minh chất lượng phân đoạn',
            'Đảm bảo quét đầy đủ hoàn thành không có lỗi',
            'Kiểm tra metadata file NIfTI để có khoảng cách chính xác',
            'Thử chạy lại quét'
        ]
    },
    {
        'problem': 'Điều Khiển Không Phản Hồi',
        'causes': [
            'Sự kiện cảm ứng không được đăng ký',
            'Vấn đề tương thích trình duyệt',
            'Mô hình vẫn đang tải'
        ],
        'solutions': [
            'Đợi mô hình tải hoàn toàn',
            'Thử làm mới trình duyệt',
            'Sử dụng điều khiển chuột thay vì cảm ứng',
            'Kiểm tra console trình duyệt để biết lỗi JavaScript'
        ]
    }
]

for issue in issues:
    document.add_heading(issue['problem'], 2)
    
    document.add_heading('Nguyên Nhân Có Thể:', 3)
    for cause in issue['causes']:
        document.add_paragraph(cause, style='List Bullet')
    
    document.add_heading('Giải Pháp:', 3)
    for solution in issue['solutions']:
        p = document.add_paragraph(solution, style='List Bullet')
        p.runs[0].font.color.rgb = RGBColor(0, 128, 0)

document.add_page_break()

# ============================================================================
# 11. CẢI TIẾN TƯƠNG LAI
# ============================================================================
document.add_heading('11. Cải Tiến Tương Lai', 1)

document.add_heading('Tính Năng Đã Lên Kế Hoạch', 2)

enhancements = [
    {
        'category': 'Cải Tiến Trực Quan Hóa',
        'items': [
            'Mặt phẳng cắt cho chế độ xem mặt cắt ngang',
            'Thanh trượt độ trong suốt có thể điều chỉnh',
            'Nhiều chế độ chiếu sáng (ambient, directional, spotlight)',
            'Sơ đồ màu tùy chỉnh cho cơ quan',
            'Hoạt ảnh: chế độ tự động xoay',
            'Chụp ảnh màn hình và ghi video'
        ]
    },
    {
        'category': 'Đo Lường và Phân Tích',
        'items': [
            'Tính toán thể tích khối u (mm³)',
            'Đo khoảng cách giữa các điểm',
            'Tính toán diện tích bề mặt',
            'Phần trăm gánh nặng khối u',
            'Theo dõi tăng trưởng qua nhiều lần quét'
        ]
    },
    {
        'category': 'Xuất và Chia Sẻ',
        'items': [
            'Xuất STL để in 3D',
            'Xuất định dạng OBJ',
            'Xuất ảnh chụp màn hình độ phân giải cao',
            'Tạo liên kết chia sẻ',
            'Báo cáo PDF với ảnh chụp 3D'
        ]
    },
    {
        'category': 'Render Nâng Cao',
        'items': [
            'Hỗ trợ VR/AR sử dụng WebXR',
            'Tải tiến trình (xem trước độ phân giải thấp trước)',
            'Render mức độ chi tiết (LOD)',
            'Ambient occlusion để cảm nhận độ sâu tốt hơn',
            'Bóng đổ và phản chiếu'
        ]
    },
    {
        'category': 'Trải Nghiệm Người Dùng',
        'items': [
            'Nhiều chế độ xem (so sánh cạnh nhau)',
            'Công cụ chú thích (đánh dấu vùng quan tâm)',
            'Đánh dấu góc nhìn yêu thích',
            'Chế độ hướng dẫn cho người dùng lần đầu',
            'Phím tắt cho người dùng chuyên nghiệp'
        ]
    },
    {
        'category': 'Cải Thiện Hiệu Suất',
        'items': [
            'Web Workers cho xử lý nền',
            'Cache mô hình để xem lại',
            'Stream dữ liệu mesh theo khối',
            'Tăng tốc GPU sử dụng TensorFlow.js',
            'Thuật toán nén mesh tối ưu'
        ]
    }
]

for enhancement in enhancements:
    document.add_heading(enhancement['category'], 3)
    for item in enhancement['items']:
        document.add_paragraph(item, style='List Bullet')

document.add_heading('Lộ Trình Phát Triển', 2)

roadmap_table = document.add_table(rows=4, cols=3)
roadmap_table.style = 'Medium Grid 3 Accent 1'

headers = roadmap_table.rows[0].cells
headers[0].text = 'Giai Đoạn'
headers[1].text = 'Thời Gian'
headers[2].text = 'Tính Năng'

roadmap = [
    ('Giai Đoạn 2', 'Q2 2026', 'Đo lường, xuất STL, điều khiển độ trong suốt'),
    ('Giai Đoạn 3', 'Q3 2026', 'Mặt phẳng cắt, nhiều chế độ xem, chú thích'),
    ('Giai Đoạn 4', 'Q4 2026', 'Hỗ trợ VR/AR, render nâng cao, caching')
]

for i, (phase, timeline, features) in enumerate(roadmap, start=1):
    row = roadmap_table.rows[i].cells
    row[0].text = phase
    row[1].text = timeline
    row[2].text = features

document.add_page_break()

# ============================================================================
# PHỤ LỤC
# ============================================================================
document.add_heading('Phụ Lục A: Thông Số Kỹ Thuật', 1)

spec_table = document.add_table(rows=11, cols=2)
spec_table.style = 'Light List Accent 1'

headers = spec_table.rows[0].cells
headers[0].text = 'Thông Số'
headers[1].text = 'Giá Trị'

specs = [
    ('Ngôn Ngữ Backend', 'Python 3.10+'),
    ('Framework Frontend', 'Flutter 3.x (Web)'),
    ('Thuật Toán 3D', 'Marching Cubes (Lorensen & Cline, 1987)'),
    ('Định Dạng 3D', 'glTF 2.0 (Binary)'),
    ('Engine Render', 'WebGL 2.0 qua flutter_3d_controller'),
    ('Đơn Giản Hóa Mesh', 'Quadric Decimation'),
    ('Số Mặt Mesh Mặc Định', 'Tụy: 10,000 | Khối U: 5,000'),
    ('Mã Hóa Truyền', 'Base64'),
    ('Timeout HTTP', '120 giây'),
    ('Trình Duyệt Hỗ Trợ', 'Chrome, Edge, Firefox, Safari (với WebGL)')
]

for i, (spec, value) in enumerate(specs, start=1):
    row = spec_table.rows[i].cells
    row[0].text = spec
    row[1].text = value

document.add_page_break()

# ============================================================================
# KẾT LUẬN
# ============================================================================
document.add_heading('Kết Luận', 1)

conclusion_text = [
    'Tính năng trực quan hóa 3D đã tích hợp thành công các kỹ thuật đồ họa máy tính '
    'tiên tiến với hình ảnh y khoa để cung cấp cho bác sĩ lâm sàng một công cụ trực quan, '
    'tương tác để kiểm tra giải phẫu tụy và bệnh lý.',
    
    'Bằng cách tận dụng các thuật toán chuẩn công nghiệp (Marching Cubes), định dạng (glTF), '
    'và công nghệ (WebGL), triển khai đạt được kết quả chất lượng chuyên nghiệp trong khi '
    'duy trì hiệu suất tuyệt vời trong trình duyệt web.',
    
    'Kiến trúc hệ thống được thiết kế để mở rộng, cho phép các cải tiến tương lai như '
    'đo lường, chú thích và kỹ thuật render nâng cao được thêm vào một cách liền mạch.',
    
    'Tài liệu này đóng vai trò là hướng dẫn toàn diện để hiểu, sử dụng và mở rộng '
    'khả năng trực quan hóa 3D của hệ thống phát hiện khối u tụy.'
]

for text in conclusion_text:
    document.add_paragraph(text)

document.add_paragraph()
document.add_paragraph()

# Signature section
signature = document.add_paragraph()
signature.add_run('Phiên Bản Tài Liệu: ').bold = True
signature.add_run('1.0\n')
signature.add_run('Cập Nhật Lần Cuối: ').bold = True
signature.add_run('20 Tháng 1, 2026\n')
signature.add_run('Trạng Thái: ').bold = True
run = signature.add_run('Hoàn Chỉnh và Sẵn Sàng Đưa Vào Sử Dụng')
run.font.color.rgb = RGBColor(0, 176, 80)
run.bold = True

# Save the document
output_file = '3D_Viewer_Implementation_Documentation_Vietnamese.docx'
document.save(output_file)
print(f"\n✓ Tài liệu tiếng Việt đã được tạo thành công!")
print(f"  File: {output_file}")
print(f"  Kích thước: ~25-30 trang")
print(f"  Phần: 11 phần chính + phụ lục")
print(f"  Bảng: 10+ bảng được định dạng")
print(f"  Danh sách: 50+ danh sách bullet/đánh số")
