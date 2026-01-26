"""
Add diagrams to corresponding sections in Vietnamese 3D Viewer documentation
"""
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def insert_diagram_after_heading(doc, heading_text, image_path, caption):
    """Insert diagram after a specific heading in the document"""
    if not os.path.exists(image_path):
        print(f"⚠ Warning: Image not found: {image_path}")
        return False
    
    found = False
    # Find the heading paragraph
    for i, para in enumerate(doc.paragraphs):
        if heading_text.lower() in para.text.lower():
            found = True
            print(f"✓ Found section: {para.text[:60]}...")
            
            # Insert diagram after the heading and its immediate descriptive paragraphs
            # We'll insert after 1-2 paragraphs to allow for section intro
            insert_position = i + 2
            
            # Create new paragraph for caption
            caption_para = doc.paragraphs[insert_position]._element
            caption_p = caption_para.getparent().insert(
                list(caption_para.getparent()).index(caption_para),
                doc.add_paragraph()._element
            )
            
            # Get the newly inserted paragraph
            new_para_index = insert_position
            
            # Find the actual paragraph object
            for idx, p in enumerate(doc.paragraphs):
                if idx == new_para_index:
                    # Add caption
                    p.text = caption
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(10)
                        run.font.italic = True
                        run.font.bold = True
                    break
            
            # Add image paragraph
            img_para = doc.paragraphs[new_para_index + 1]._element
            img_p = img_para.getparent().insert(
                list(img_para.getparent()).index(img_para),
                doc.add_paragraph()._element
            )
            
            # Find the image paragraph and add picture
            for idx, p in enumerate(doc.paragraphs):
                if idx == new_para_index + 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run = p.add_run()
                    try:
                        run.add_picture(image_path, width=Inches(6.0))
                        print(f"  → Inserted: {caption}")
                    except Exception as e:
                        print(f"  ✗ Error inserting image: {e}")
                    break
            
            # Add spacing
            spacing_para = doc.paragraphs[new_para_index + 2]._element
            spacing_p = spacing_para.getparent().insert(
                list(spacing_para.getparent()).index(spacing_para),
                doc.add_paragraph()._element
            )
            
            break
    
    if not found:
        print(f"⚠ Section not found for: {heading_text}")
    
    return found

def insert_diagram_at_position(doc, position_index, image_path, caption):
    """Insert diagram at a specific position in the document"""
    if not os.path.exists(image_path):
        print(f"⚠ Warning: Image not found: {image_path}")
        return
    
    # Add caption
    caption_para = doc.add_paragraph()
    caption_para.text = caption
    caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in caption_para.runs:
        run.font.size = Pt(10)
        run.font.italic = True
        run.font.bold = True
    
    # Add image
    img_para = doc.add_paragraph()
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    try:
        run.add_picture(image_path, width=Inches(6.0))
        print(f"✓ Inserted at position {position_index}: {caption}")
    except Exception as e:
        print(f"✗ Error inserting image: {e}")
    
    # Add spacing
    doc.add_paragraph()

def main():
    print("\n" + "="*70)
    print("Thêm Diagrams Vào Các Phần Tương Ứng Trong Tài Liệu")
    print("="*70 + "\n")
    
    # Input and output paths
    input_doc = r"Research Paper\3D_Viewer_Documentation_Vietnamese_Updated.docx"
    output_doc = r"Research Paper\3D_Viewer_Documentation_Vietnamese_With_Diagrams.docx"
    
    # Check if input exists
    if not os.path.exists(input_doc):
        print(f"✗ Error: Input document not found: {input_doc}")
        return
    
    # Load the document
    print(f"Loading: {input_doc}\n")
    doc = Document(input_doc)
    
    # Show document structure
    print("Document structure:")
    for i, para in enumerate(doc.paragraphs[:30]):  # First 30 paragraphs
        if para.style.name.startswith('Heading'):
            print(f"  [{i}] {para.style.name}: {para.text[:60]}")
    print()
    
    # Define diagrams with their target sections (based on heading keywords)
    diagrams = [
        {
            "heading_keywords": "kiến trúc",
            "path": r"Diagram\Image\Kiến trúc hệ thống 3d viewer.drawio.png",
            "caption": "Hình 1: Kiến Trúc Hệ Thống 3D Viewer"
        },
        {
            "heading_keywords": "pipeline",
            "path": r"Diagram\Image\Pipeline Xử Lý CT Volume.drawio.png",
            "caption": "Hình 2: Pipeline Xử Lý CT Volume"
        },
        {
            "heading_keywords": "marching cubes",
            "path": r"Diagram\Image\Thuật Toán Marching Cubes.drawio.png",
            "caption": "Hình 3: Thuật Toán Marching Cubes"
        },
        {
            "heading_keywords": "u-net",
            "path": r"Diagram\Image\Kiến Trúc U-Net.drawio.png",
            "caption": "Hình 4: Kiến Trúc U-Net"
        },
        {
            "heading_keywords": "webgl",
            "path": r"Diagram\Image\Pipeline WebGL Rendering.drawio.png",
            "caption": "Hình 5: Pipeline WebGL Rendering"
        }
    ]
    
    # Try to insert each diagram in its corresponding section
    print("Inserting diagrams:\n")
    for diagram in diagrams:
        insert_diagram_after_heading(
            doc,
            diagram["heading_keywords"],
            diagram["path"],
            diagram["caption"]
        )
    
    # Save the document
    print(f"\n{'='*70}")
    print(f"Saving: {output_doc}")
    doc.save(output_doc)
    
    print(f"✓ Hoàn Tất! Tài liệu đã được lưu tại:")
    print(f"  {output_doc}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
