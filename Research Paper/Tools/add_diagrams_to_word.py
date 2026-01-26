"""
Add diagrams to Vietnamese 3D Viewer documentation
"""
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def add_diagram_section(doc, title, image_path, description=""):
    """Add a diagram with title and optional description"""
    if not os.path.exists(image_path):
        print(f"⚠ Warning: Image not found: {image_path}")
        return
    
    # Add heading
    heading = doc.add_heading(title, level=2)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add description if provided
    if description:
        desc_para = doc.add_paragraph(description)
        desc_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in desc_para.runs:
            run.font.size = Pt(11)
            run.font.italic = True
    
    # Add image centered
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    
    # Add picture with width of 6 inches (preserves aspect ratio)
    try:
        run.add_picture(image_path, width=Inches(6.0))
        print(f"✓ Added: {title}")
    except Exception as e:
        print(f"✗ Error adding {title}: {e}")
    
    # Add spacing after diagram
    doc.add_paragraph()

def main():
    print("\n" + "="*70)
    print("Thêm Diagrams Vào Tài Liệu Word")
    print("="*70 + "\n")
    
    # Input and output paths
    input_doc = r"Research Paper\3D_Viewer_Documentation_Vietnamese_Updated.docx"
    output_doc = r"Research Paper\3D_Viewer_Documentation_Vietnamese_With_Diagrams.docx"
    
    # Check if input exists
    if not os.path.exists(input_doc):
        print(f"✗ Error: Input document not found: {input_doc}")
        return
    
    # Load the document
    print(f"Loading: {input_doc}")
    doc = Document(input_doc)
    
    # Diagram paths (in order)
    diagrams = [
        {
            "title": "Hình 1: Kiến Trúc Hệ Thống 3D Viewer",
            "path": r"Diagram\Image\Kiến trúc hệ thống 3d viewer.drawio.png",
            "description": "Tổng quan kiến trúc hệ thống với Flutter frontend, Python backend và lưu trữ dữ liệu"
        },
        {
            "title": "Hình 2: Pipeline Xử Lý CT Volume → 3D Rendering",
            "path": r"Diagram\Image\Pipeline Xử Lý CT Volume.drawio.png",
            "description": "Quy trình xử lý từ file NIfTI đến hiển thị 3D tương tác"
        },
        {
            "title": "Hình 3: Thuật Toán Marching Cubes",
            "path": r"Diagram\Image\Thuật Toán Marching Cubes.drawio.png",
            "description": "Chi tiết thuật toán tạo mesh 3D từ volume data"
        },
        {
            "title": "Hình 4: Kiến Trúc U-Net",
            "path": r"Diagram\Image\Kiến Trúc U-Net.drawio.png",
            "description": "Mạng neural U-Net cho phân đoạn tụy và khối u"
        },
        {
            "title": "Hình 5: Pipeline WebGL Rendering",
            "path": r"Diagram\Image\Pipeline WebGL Rendering.drawio.png",
            "description": "Quy trình render 3D trong trình duyệt sử dụng WebGL"
        }
    ]
    
    # Add page break before diagrams section
    doc.add_page_break()
    
    # Add main section heading
    main_heading = doc.add_heading('PHỤ LỤC: CÁC SƠ ĐỒ MINH HỌA', level=1)
    main_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add intro paragraph
    intro = doc.add_paragraph(
        "Các sơ đồ dưới đây minh họa chi tiết kiến trúc hệ thống, quy trình xử lý dữ liệu, "
        "và các thuật toán được sử dụng trong module 3D Viewer."
    )
    intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in intro.runs:
        run.font.size = Pt(11)
    
    doc.add_paragraph()
    
    # Add each diagram
    for diagram in diagrams:
        add_diagram_section(doc, diagram["title"], diagram["path"], diagram["description"])
    
    # Save the document
    print(f"\nSaving: {output_doc}")
    doc.save(output_doc)
    
    print("\n" + "="*70)
    print(f"✓ Hoàn Tất! Tài liệu đã được lưu tại:")
    print(f"  {output_doc}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
