"""
Create diagrams for 3D Viewer documentation using matplotlib
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

# Set style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

# ============================================================================
# DIAGRAM 1: System Architecture
# ============================================================================
def create_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Kiến Trúc Hệ Thống 3D Viewer', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Flutter Frontend
    flutter_box = FancyBboxPatch((0.5, 6), 4, 2.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#42A5F5', 
                                  edgecolor='#1976D2', 
                                  linewidth=2)
    ax.add_patch(flutter_box)
    ax.text(2.5, 8, 'FLUTTER WEB CLIENT', ha='center', fontsize=12, 
            fontweight='bold', color='white')
    
    # Flutter components
    components = [
        (1, 7.3, 'File Upload\nWidget'),
        (2.5, 7.3, '2D Viewer\n(Slices)'),
        (4, 7.3, '3D Viewer\n(Three.js)')
    ]
    for x, y, label in components:
        box = Rectangle((x-0.4, y-0.3), 0.8, 0.5, 
                       facecolor='white', edgecolor='#1976D2')
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8)
    
    # Python Backend
    python_box = FancyBboxPatch((0.5, 2.5), 4, 2.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#66BB6A', 
                                 edgecolor='#388E3C', 
                                 linewidth=2)
    ax.add_patch(python_box)
    ax.text(2.5, 4.6, 'PYTHON BACKEND SERVER', ha='center', fontsize=12, 
            fontweight='bold', color='white')
    
    # Backend components
    backend_comps = [
        (1, 3.8, 'NIfTI\nLoader'),
        (1.8, 3.8, 'U-Net\nModels'),
        (2.6, 3.8, 'Marching\nCubes'),
        (3.4, 3.8, '3D Mesh\nExport')
    ]
    for x, y, label in backend_comps:
        box = Rectangle((x-0.35, y-0.3), 0.7, 0.5, 
                       facecolor='white', edgecolor='#388E3C')
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=7)
    
    backend_comps2 = [
        (1, 3.1, 'HU\nWindowing'),
        (1.8, 3.1, 'Context\nAware'),
        (2.6, 3.1, 'Mesh\nSimplify'),
        (3.4, 3.1, 'glTF\nExport')
    ]
    for x, y, label in backend_comps2:
        box = Rectangle((x-0.35, y-0.3), 0.7, 0.5, 
                       facecolor='white', edgecolor='#388E3C')
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=7)
    
    # Communication arrow
    arrow = FancyArrowPatch((2.5, 6), (2.5, 5), 
                           arrowstyle='<->', mutation_scale=20, 
                           linewidth=2, color='#FF6F00')
    ax.add_patch(arrow)
    ax.text(3.2, 5.5, 'HTTP REST API\n/generate_3d_model', 
            fontsize=9, color='#FF6F00', fontweight='bold')
    
    # Data Storage
    storage_box = FancyBboxPatch((5.5, 2.5), 3.5, 5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor='#E0E0E0', 
                                  edgecolor='#757575', 
                                  linewidth=2)
    ax.add_patch(storage_box)
    ax.text(7.25, 7.2, 'DỮ LIỆU', ha='center', fontsize=12, 
            fontweight='bold', color='#424242')
    
    # Data items
    data_items = [
        (7.25, 6.5, 'CT Volume (NIfTI)'),
        (7.25, 5.9, '512×512×200 slices'),
        (7.25, 5.3, '3D Mask Arrays'),
        (7.25, 4.7, 'Pancreas: 256×256×N'),
        (7.25, 4.1, 'Tumor: 256×256×N'),
        (7.25, 3.5, '3D Meshes'),
        (7.25, 2.9, 'Vertices + Faces')
    ]
    for x, y, label in data_items:
        ax.text(x, y, label, ha='center', fontsize=9)
    
    # Arrows to data
    arrow1 = FancyArrowPatch((4.5, 7.2), (5.5, 7.2), 
                            arrowstyle='->', mutation_scale=15, 
                            linewidth=1.5, color='#757575')
    ax.add_patch(arrow1)
    
    arrow2 = FancyArrowPatch((4.5, 3.5), (5.5, 3.5), 
                            arrowstyle='->', mutation_scale=15, 
                            linewidth=1.5, color='#757575')
    ax.add_patch(arrow2)
    
    # Legend
    legend_elements = [
        mpatches.Patch(color='#42A5F5', label='Frontend (Flutter)'),
        mpatches.Patch(color='#66BB6A', label='Backend (Python)'),
        mpatches.Patch(color='#E0E0E0', label='Dữ Liệu')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('diagram_1_system_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ Diagram 1: System Architecture saved")
    plt.close()

# ============================================================================
# DIAGRAM 2: Data Flow Pipeline
# ============================================================================
def create_data_flow_pipeline():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(7, 11.5, 'Pipeline Xử Lý CT Volume → 3D Rendering', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Steps with colors
    steps = [
        (7, 10, 'NIfTI File\n.nii/.nii.gz', '#FF6B6B'),
        (7, 8.5, 'Load Volume\n512×512×200', '#4ECDC4'),
        (7, 7, 'HU Windowing\n-150 to 250 HU', '#45B7D1'),
        (3.5, 5.5, 'Slice Extraction\n2D Images', '#96CEB4'),
        (3.5, 4, 'U-Net Pancreas\n256×256 Mask', '#FFEAA7'),
        (10.5, 5.5, 'Slice Processing\nLoop Z=0 to N', '#DFE6E9'),
        (10.5, 4, 'U-Net Tumor\n128×128 Mask', '#FFEAA7'),
        (7, 2.5, '3D Mask Volume\n256×256×N', '#74B9FF'),
        (7, 1, 'Marching Cubes\nMesh Generation', '#A29BFE'),
        (3.5, -0.5, 'Mesh Processing\nSimplification', '#FD79A8'),
        (10.5, -0.5, 'glTF Export\nBase64 Encode', '#FDCB6E'),
        (7, -2, '3D Viewer (WebGL)\nInteractive Render', '#00B894')
    ]
    
    for x, y, label, color in steps:
        box = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.7, 
                            boxstyle="round,pad=0.05", 
                            facecolor=color, 
                            edgecolor='black', 
                            linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', 
               fontsize=9, fontweight='bold')
    
    # Arrows
    arrows = [
        (7, 9.6, 7, 8.9),
        (7, 8.1, 7, 7.4),
        (7, 6.6, 3.5, 5.9),
        (7, 6.6, 10.5, 5.9),
        (3.5, 5.1, 3.5, 4.4),
        (10.5, 5.1, 10.5, 4.4),
        (3.5, 3.6, 7, 2.9),
        (10.5, 3.6, 7, 2.9),
        (7, 2.1, 7, 1.4),
        (7, 0.6, 3.5, -0.1),
        (7, 0.6, 10.5, -0.1),
        (3.5, -0.9, 7, -1.6),
        (10.5, -0.9, 7, -1.6)
    ]
    
    for x1, y1, x2, y2 in arrows:
        arrow = FancyArrowPatch((x1, y1), (x2, y2), 
                               arrowstyle='->', mutation_scale=20, 
                               linewidth=2, color='#2C3E50')
        ax.add_patch(arrow)
    
    # Annotations
    annotations = [
        (11.5, 7, 'Mỗi slice được\nxử lý độc lập', 8),
        (1.5, 4, 'Phân đoạn\ntụy trước', 8),
        (12.5, 4, 'Sau đó phát\nhiện khối u', 8),
        (1.5, -0.5, 'Giảm số\npolygon', 8),
        (12.5, -0.5, 'Đóng gói\nvà truyền', 8)
    ]
    
    for x, y, text, size in annotations:
        ax.text(x, y, text, ha='center', fontsize=size, 
               style='italic', color='#636E72')
    
    # Time indicators
    ax.text(0.5, 5.5, '~200ms/slice', fontsize=8, color='red', fontweight='bold')
    ax.text(0.5, 2.5, '~5-15s total', fontsize=8, color='red', fontweight='bold')
    ax.text(0.5, 1, '~2-5s', fontsize=8, color='red', fontweight='bold')
    ax.text(0.5, -0.5, '~1-3s', fontsize=8, color='red', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('diagram_2_data_flow_pipeline.png', dpi=300, bbox_inches='tight')
    print("✓ Diagram 2: Data Flow Pipeline saved")
    plt.close()

# ============================================================================
# DIAGRAM 3: Marching Cubes Algorithm
# ============================================================================
def create_marching_cubes():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Thuật Toán Marching Cubes', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Step 1: 3D Volume
    ax.text(2, 8.5, 'Bước 1: Volume 3D', ha='center', fontsize=11, fontweight='bold')
    # Draw 3D grid representation
    for i in range(4):
        for j in range(4):
            x_offset = 0.5 + i*0.3
            y_offset = 7.2 + j*0.3 - i*0.15
            rect = Rectangle((x_offset, y_offset), 0.25, 0.25, 
                           facecolor='lightblue' if (i+j)%2 else 'lightcoral',
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
    
    ax.text(2, 6.5, '256×256×N voxels', ha='center', fontsize=9, style='italic')
    
    # Arrow
    arrow1 = FancyArrowPatch((3.5, 7.5), (4.5, 7.5), 
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=2, color='black')
    ax.add_patch(arrow1)
    
    # Step 2: Cube extraction
    ax.text(6, 8.5, 'Bước 2: Chia Thành Khối', ha='center', fontsize=11, fontweight='bold')
    
    # Draw a cube with vertices
    cube_vertices = [
        (5.2, 6.8), (5.8, 6.8), (6.2, 7.2), (5.6, 7.2),
        (5.2, 7.5), (5.8, 7.5), (6.2, 7.9), (5.6, 7.9)
    ]
    
    # Draw cube edges
    edges = [(0,1), (1,2), (2,3), (3,0),  # bottom
             (4,5), (5,6), (6,7), (7,4),  # top
             (0,4), (1,5), (2,6), (3,7)]  # vertical
    
    for e1, e2 in edges:
        ax.plot([cube_vertices[e1][0], cube_vertices[e2][0]], 
               [cube_vertices[e1][1], cube_vertices[e2][1]], 
               'b-', linewidth=2)
    
    # Draw vertices with inside/outside indication
    for i, (x, y) in enumerate(cube_vertices):
        color = 'green' if i % 2 == 0 else 'red'
        circle = Circle((x, y), 0.08, facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
    
    ax.text(6, 6.3, '8 đỉnh: trong (xanh) / ngoài (đỏ)', 
           ha='center', fontsize=8, style='italic')
    
    # Arrow
    arrow2 = FancyArrowPatch((7, 7.5), (8, 7.5), 
                            arrowstyle='->', mutation_scale=20, 
                            linewidth=2, color='black')
    ax.add_patch(arrow2)
    
    # Step 3: Triangle generation
    ax.text(10, 8.5, 'Bước 3: Tạo Tam Giác', ha='center', fontsize=11, fontweight='bold')
    
    # Draw triangulated surface
    triangle_points = [
        [(9, 7.5), (9.5, 7.2), (9.5, 7.8)],
        [(9.5, 7.2), (10, 7.5), (9.5, 7.8)],
        [(10, 7.5), (10.5, 7.2), (10.5, 7.8)],
        [(10.5, 7.2), (11, 7.5), (10.5, 7.8)]
    ]
    
    for triangle in triangle_points:
        tri = plt.Polygon(triangle, facecolor='yellow', 
                         edgecolor='black', linewidth=2, alpha=0.7)
        ax.add_patch(tri)
    
    ax.text(10, 6.5, '2⁸ = 256 cấu hình', ha='center', fontsize=9, style='italic')
    
    # Bottom section: Process explanation
    process_y = 5
    ax.text(6, process_y, 'Quy Trình Chi Tiết', ha='center', 
           fontsize=13, fontweight='bold', color='#2C3E50')
    
    process_steps = [
        '1. Chia volume thành các ô khối 2×2×2 (8 đỉnh mỗi khối)',
        '2. Với mỗi đỉnh: kiểm tra giá trị > threshold (0.5) → đánh dấu trong/ngoài',
        '3. Tạo 8-bit index từ trạng thái 8 đỉnh (ví dụ: 10110100)',
        '4. Tra lookup table để lấy cấu hình tam giác tương ứng',
        '5. Nội suy vị trí đỉnh chính xác dọc theo cạnh khối',
        '6. Tạo vertices (tọa độ x,y,z) và faces (chỉ số 3 đỉnh)',
        '7. Tính normal vectors cho mỗi đỉnh (để lighting)',
        '8. Áp dụng spacing để chuyển từ voxel space → physical space (mm)'
    ]
    
    y_pos = process_y - 0.7
    for step in process_steps:
        ax.text(0.5, y_pos, step, fontsize=9, va='top')
        y_pos -= 0.4
    
    # Output box
    output_box = FancyBboxPatch((1, 0.5), 10, 1.2, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#E8F5E9', 
                                edgecolor='#4CAF50', 
                                linewidth=2)
    ax.add_patch(output_box)
    
    ax.text(6, 1.4, 'OUTPUT', ha='center', fontsize=11, fontweight='bold')
    output_text = [
        'Vertices: Mảng Mx3 (ví dụ: 50,000 × 3 = 150,000 giá trị)',
        'Faces: Mảng Kx3 (ví dụ: 100,000 × 3 = 300,000 chỉ số)',
        'Normals: Mảng Mx3 (vector pháp tuyến cho lighting)'
    ]
    y_pos = 1.1
    for text in output_text:
        ax.text(6, y_pos, text, ha='center', fontsize=8)
        y_pos -= 0.25
    
    plt.tight_layout()
    plt.savefig('diagram_3_marching_cubes.png', dpi=300, bbox_inches='tight')
    print("✓ Diagram 3: Marching Cubes saved")
    plt.close()

# ============================================================================
# DIAGRAM 4: U-Net Architecture
# ============================================================================
def create_unet_architecture():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Kiến Trúc U-Net Cho Phân Đoạn', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Input
    input_box = Rectangle((1, 4), 1, 1.5, facecolor='#E8EAF6', 
                         edgecolor='#3F51B5', linewidth=2)
    ax.add_patch(input_box)
    ax.text(1.5, 4.75, 'Input\n256×256×1', ha='center', va='center', fontsize=9)
    
    # Encoder (downsampling path)
    encoder_blocks = [
        (3, 4.2, 0.8, 1.1, '64', '#BBDEFB'),
        (4.5, 4.4, 0.7, 0.9, '128', '#90CAF9'),
        (6, 4.6, 0.6, 0.7, '256', '#64B5F6'),
        (7.5, 4.8, 0.5, 0.5, '512', '#42A5F5')
    ]
    
    for x, y, w, h, filters, color in encoder_blocks:
        box = Rectangle((x, y), w, h, facecolor=color, 
                       edgecolor='#1976D2', linewidth=2)
        ax.add_patch(box)
        ax.text(x+w/2, y+h/2, f'{filters}\nfilters', ha='center', va='center', fontsize=8)
        
        # MaxPooling arrow
        if x < 7.5:
            arrow = FancyArrowPatch((x+w, y+h/2), (x+w+0.5, y+h/2+0.1), 
                                   arrowstyle='->', mutation_scale=15, 
                                   linewidth=1.5, color='red')
            ax.add_patch(arrow)
            ax.text(x+w+0.3, y+h/2-0.3, '2×2\npool', ha='center', fontsize=6, color='red')
    
    # Bottleneck
    bottleneck = Rectangle((8.5, 5), 0.4, 0.4, facecolor='#1976D2', 
                          edgecolor='#0D47A1', linewidth=2)
    ax.add_patch(bottleneck)
    ax.text(8.7, 5.2, '1024', ha='center', va='center', fontsize=8, color='white')
    
    # Decoder (upsampling path)
    decoder_blocks = [
        (10, 4.8, 0.5, 0.5, '512', '#42A5F5'),
        (11, 4.6, 0.6, 0.7, '256', '#64B5F6'),
        (12, 4.4, 0.7, 0.9, '128', '#90CAF9'),
        (13, 4.2, 0.8, 1.1, '64', '#BBDEFB')
    ]
    
    for x, y, w, h, filters, color in decoder_blocks:
        box = Rectangle((x, y), w, h, facecolor=color, 
                       edgecolor='#1976D2', linewidth=2)
        ax.add_patch(box)
        ax.text(x+w/2, y+h/2, f'{filters}\nfilters', ha='center', va='center', fontsize=8)
        
        # Upsampling arrow
        if x > 10:
            arrow = FancyArrowPatch((x-0.5, y+h/2+0.1), (x, y+h/2), 
                                   arrowstyle='->', mutation_scale=15, 
                                   linewidth=1.5, color='green')
            ax.add_patch(arrow)
            ax.text(x-0.3, y+h/2+0.4, '2×2\nup', ha='center', fontsize=6, color='green')
    
    # Bottleneck arrows
    arrow_down = FancyArrowPatch((8, 5), (8.5, 5.2), 
                                arrowstyle='->', mutation_scale=15, 
                                linewidth=1.5, color='red')
    ax.add_patch(arrow_down)
    
    arrow_up = FancyArrowPatch((8.9, 5.2), (10, 5.1), 
                              arrowstyle='->', mutation_scale=15, 
                              linewidth=1.5, color='green')
    ax.add_patch(arrow_up)
    
    # Skip connections
    skip_connections = [
        (3.4, 4.75, 13.4, 4.75),
        (5.15, 5.05, 11.3, 5.05),
        (6.3, 5.25, 10.3, 5.25)
    ]
    
    for x1, y1, x2, y2 in skip_connections:
        # Draw curved arrow
        arrow = FancyArrowPatch((x1, y1), (x2, y2), 
                               arrowstyle='->', mutation_scale=12,
                               connectionstyle="arc3,rad=.3",
                               linewidth=1.5, color='#FF6F00', linestyle='--')
        ax.add_patch(arrow)
    
    ax.text(7, 6.5, 'Skip Connections', ha='center', fontsize=9, 
           color='#FF6F00', fontweight='bold', style='italic')
    
    # Output
    output_box = Rectangle((14.2, 4), 1, 1.5, facecolor='#C8E6C9', 
                          edgecolor='#4CAF50', linewidth=2)
    ax.add_patch(output_box)
    ax.text(14.7, 4.75, 'Output\n256×256×1\nMask', ha='center', va='center', fontsize=9)
    
    # Arrow to output
    arrow_out = FancyArrowPatch((13.8, 4.75), (14.2, 4.75), 
                               arrowstyle='->', mutation_scale=15, 
                               linewidth=2, color='black')
    ax.add_patch(arrow_out)
    
    # Labels
    ax.text(1.5, 3, 'Input Layer', ha='center', fontsize=10, fontweight='bold')
    ax.text(5.5, 3, 'Encoder\n(Downsampling)', ha='center', fontsize=10, 
           fontweight='bold', color='#D32F2F')
    ax.text(8.7, 3.5, 'Bottleneck', ha='center', fontsize=10, fontweight='bold')
    ax.text(11.5, 3, 'Decoder\n(Upsampling)', ha='center', fontsize=10, 
           fontweight='bold', color='#388E3C')
    ax.text(14.7, 3, 'Output Layer', ha='center', fontsize=10, fontweight='bold')
    
    # Legend
    legend_y = 1.5
    ax.text(7, legend_y+0.5, 'Các Thành Phần:', ha='center', fontsize=11, fontweight='bold')
    
    legend_items = [
        (3, legend_y, 'Conv 3×3 + ReLU', '#BBDEFB'),
        (5.5, legend_y, 'MaxPool 2×2 ↓', 'red'),
        (8, legend_y, 'UpSample 2×2 ↑', 'green'),
        (10.5, legend_y, 'Skip Connection →', '#FF6F00')
    ]
    
    for x, y, label, color in legend_items:
        if color in ['red', 'green', '#FF6F00']:
            ax.plot([x-0.3, x-0.1], [y, y], color=color, linewidth=3)
        else:
            box = Rectangle((x-0.35, y-0.1), 0.3, 0.2, facecolor=color, edgecolor='black')
            ax.add_patch(box)
        ax.text(x+0.2, y, label, fontsize=8, va='center')
    
    plt.tight_layout()
    plt.savefig('diagram_4_unet_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ Diagram 4: U-Net Architecture saved")
    plt.close()

# ============================================================================
# DIAGRAM 5: WebGL Rendering Pipeline
# ============================================================================
def create_webgl_pipeline():
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Title
    ax.text(5, 13.5, 'Pipeline WebGL Rendering', 
            ha='center', fontsize=16, fontweight='bold')
    
    # Steps
    steps = [
        (5, 12, 'glTF Binary Data\n(Base64 Decoded)', '#FF6B6B', 1.5),
        (5, 10, 'Parse glTF Structure\nVertices, Faces, Materials', '#4ECDC4', 1.5),
        (5, 8, 'Create WebGL Buffers\nVertex Buffer, Index Buffer', '#45B7D1', 1.5),
        (5, 6, 'Compile Shaders\nVertex + Fragment Shaders', '#96CEB4', 1.5),
        (5, 4, 'Setup Scene\nCamera, Lights, Materials', '#FFEAA7', 1.5),
        (5, 2, 'Render Loop (60 FPS)\nDraw Calls + User Input', '#74B9FF', 1.5),
        (5, 0, '3D Interactive View\nRotate, Zoom, Pan', '#00B894', 1.5)
    ]
    
    for i, (x, y, label, color, h) in enumerate(steps):
        box = FancyBboxPatch((x-1.8, y-h/2), 3.6, h, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, 
                            edgecolor='black', 
                            linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', 
               fontsize=10, fontweight='bold')
        
        # Arrow to next step
        if i < len(steps) - 1:
            arrow = FancyArrowPatch((x, y-h/2-0.1), (x, steps[i+1][1]+steps[i+1][4]/2+0.1), 
                                   arrowstyle='->', mutation_scale=25, 
                                   linewidth=2.5, color='#2C3E50')
            ax.add_patch(arrow)
    
    # Side annotations
    annotations = [
        (8.5, 12, 'Flutter 3D\nController', 9),
        (8.5, 10, 'JSON\nParsing', 9),
        (8.5, 8, 'WebGL\nContext', 9),
        (8.5, 6, 'GLSL\nCode', 9),
        (8.5, 4, '3D Math\nLibraries', 9),
        (8.5, 2, 'Event\nHandlers', 9),
        (8.5, 0, 'User\nInteraction', 9)
    ]
    
    for x, y, text, size in annotations:
        # Arrow pointing to annotation
        arrow = FancyArrowPatch((6.8, y), (8, y), 
                               arrowstyle='->', mutation_scale=12, 
                               linewidth=1, color='gray')
        ax.add_patch(arrow)
        ax.text(x, y, text, ha='center', va='center', fontsize=size, 
               style='italic', color='#636E72',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Performance metrics
    metrics_box = FancyBboxPatch((0.3, 10.5), 2.5, 2.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor='#FFF3CD', 
                                 edgecolor='#856404', 
                                 linewidth=2)
    ax.add_patch(metrics_box)
    
    ax.text(1.55, 12.7, 'Hiệu Suất', ha='center', fontsize=10, fontweight='bold')
    metrics = [
        'FPS: 60',
        'Vertices: 15K',
        'Triangles: 15K',
        'Draw Calls: 2',
        'Memory: ~50MB'
    ]
    y_pos = 12.3
    for metric in metrics:
        ax.text(1.55, y_pos, metric, ha='center', fontsize=8)
        y_pos -= 0.35
    
    # Shader code example
    shader_box = FancyBboxPatch((0.3, 5.5), 2.5, 3, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#D1ECF1', 
                                edgecolor='#0C5460', 
                                linewidth=2)
    ax.add_patch(shader_box)
    
    ax.text(1.55, 8.2, 'Vertex Shader', ha='center', fontsize=9, fontweight='bold')
    shader_code = [
        'gl_Position =',
        '  projection *',
        '  view *',
        '  model *',
        '  vec4(position, 1.0);',
        '',
        'vNormal = normal;',
        'vColor = color;'
    ]
    y_pos = 7.8
    for line in shader_code:
        ax.text(0.5, y_pos, line, fontsize=7, family='monospace')
        y_pos -= 0.25
    
    plt.tight_layout()
    plt.savefig('diagram_5_webgl_pipeline.png', dpi=300, bbox_inches='tight')
    print("✓ Diagram 5: WebGL Rendering Pipeline saved")
    plt.close()

# ============================================================================
# Main execution
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Tạo Diagrams Cho Tài Liệu 3D Viewer")
    print("="*60 + "\n")
    
    create_system_architecture()
    create_data_flow_pipeline()
    create_marching_cubes()
    create_unet_architecture()
    create_webgl_pipeline()
    
    print("\n" + "="*60)
    print("✓ Hoàn Tất! Tất cả diagrams đã được tạo:")
    print("  1. diagram_1_system_architecture.png")
    print("  2. diagram_2_data_flow_pipeline.png")
    print("  3. diagram_3_marching_cubes.png")
    print("  4. diagram_4_unet_architecture.png")
    print("  5. diagram_5_webgl_pipeline.png")
    print("="*60 + "\n")
