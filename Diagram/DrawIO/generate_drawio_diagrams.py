"""
Generate Draw.io diagrams for 3D Viewer documentation
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_drawio_xml(diagram_name, page_width, page_height, cells):
    """Create a draw.io XML structure"""
    root = ET.Element('mxfile', {
        'host': 'app.diagrams.net',
        'modified': '2026-01-20T00:00:00.000Z',
        'agent': 'Python Generator',
        'version': '24.0.0'
    })
    
    diagram = ET.SubElement(root, 'diagram', {
        'name': 'Page-1',
        'id': diagram_name
    })
    
    model = ET.SubElement(diagram, 'mxGraphModel', {
        'dx': '1422',
        'dy': '762',
        'grid': '1',
        'gridSize': '10',
        'guides': '1',
        'tooltips': '1',
        'connect': '1',
        'arrows': '1',
        'fold': '1',
        'page': '1',
        'pageScale': '1',
        'pageWidth': str(page_width),
        'pageHeight': str(page_height),
        'math': '0',
        'shadow': '0'
    })
    
    root_elem = ET.SubElement(model, 'root')
    ET.SubElement(root_elem, 'mxCell', {'id': '0'})
    ET.SubElement(root_elem, 'mxCell', {'id': '1', 'parent': '0'})
    
    # Add all cells with proper geometry
    for cell_data in cells:
        geom = cell_data.pop('geometry', None)
        cell = ET.SubElement(root_elem, 'mxCell', cell_data)
        if geom:
            ET.SubElement(cell, 'mxGeometry', {k: str(v) for k, v in geom.items()})
    
    return root

def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def save_drawio(filename, xml_root):
    """Save draw.io XML to file"""
    xml_str = prettify_xml(xml_root)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"✓ Created: {filename}")

# ============================================================================
# DIAGRAM 1: System Architecture
# ============================================================================
def create_system_architecture():
    cells = [
        # Title
        {'id': 'title', 'value': 'Kiến Trúc Hệ Thống 3D Viewer', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '400', 'y': '20', 'width': '400', 'height': '40', 'as': 'geometry'}},
        
        # Flutter Frontend Container
        {'id': 'flutter_box', 'value': 'FLUTTER WEB CLIENT', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#42A5F5;strokeColor=#1976D2;strokeWidth=2;fontSize=14;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=top;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '100', 'width': '400', 'height': '250', 'as': 'geometry'}},
        
        # Flutter Components
        {'id': 'flutter1', 'value': 'File Upload\nWidget', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1976D2;fontSize=10;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '80', 'y': '160', 'width': '100', 'height': '60', 'as': 'geometry'}},
        {'id': 'flutter2', 'value': '2D Viewer\n(Slices)', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1976D2;fontSize=10;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '200', 'y': '160', 'width': '100', 'height': '60', 'as': 'geometry'}},
        {'id': 'flutter3', 'value': '3D Viewer\n(Three.js)', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1976D2;fontSize=10;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '320', 'y': '160', 'width': '100', 'height': '60', 'as': 'geometry'}},
        
        # Python Backend Container
        {'id': 'python_box', 'value': 'PYTHON BACKEND SERVER', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#66BB6A;strokeColor=#388E3C;strokeWidth=2;fontSize=14;fontStyle=1;fontColor=#FFFFFF;align=center;verticalAlign=top;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '450', 'width': '400', 'height': '250', 'as': 'geometry'}},
        
        # Backend Components Row 1
        {'id': 'backend1', 'value': 'NIfTI\nLoader', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '70', 'y': '510', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend2', 'value': 'U-Net\nModels', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '160', 'y': '510', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend3', 'value': 'Marching\nCubes', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '250', 'y': '510', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend4', 'value': '3D Mesh\nExport', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '340', 'y': '510', 'width': '80', 'height': '50', 'as': 'geometry'}},
        
        # Backend Components Row 2
        {'id': 'backend5', 'value': 'HU\nWindowing', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '70', 'y': '580', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend6', 'value': 'Context\nAware', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '160', 'y': '580', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend7', 'value': 'Mesh\nSimplify', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '250', 'y': '580', 'width': '80', 'height': '50', 'as': 'geometry'}},
        {'id': 'backend8', 'value': 'glTF\nExport', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#388E3C;fontSize=9;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '340', 'y': '580', 'width': '80', 'height': '50', 'as': 'geometry'}},
        
        # Data Storage Container
        {'id': 'data_box', 'value': 'DỮ LIỆU', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E0E0E0;strokeColor=#757575;strokeWidth=2;fontSize=14;fontStyle=1;align=center;verticalAlign=top;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '550', 'y': '100', 'width': '350', 'height': '600', 'as': 'geometry'}},
        
        # Data items
        {'id': 'data_text', 'value': 'CT Volume (NIfTI)\n512×512×200 slices\n\n3D Mask Arrays\nPancreas: 256×256×N\nTumor: 256×256×N\n\n3D Meshes\nVertices + Faces', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '575', 'y': '200', 'width': '300', 'height': '400', 'as': 'geometry'}},
        
        # Communication Arrow (Frontend <-> Backend)
        {'id': 'arrow1', 'value': 'HTTP REST API\n/generate_3d_model', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#FF6F00;fontSize=10;fontStyle=1;fontColor=#FF6F00;startArrow=classic;startFill=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'flutter_box', 'target': 'python_box', 'geometry': {'relative': '1', 'as': 'geometry'}},
        
        # Arrows to data storage
        {'id': 'arrow2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#757575;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'flutter_box', 'target': 'data_box', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow3', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#757575;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'python_box', 'target': 'data_box', 'geometry': {'relative': '1', 'as': 'geometry'}},
    ]
    
    xml = create_drawio_xml('system-architecture', 1200, 800, cells)
    save_drawio('diagram_1_system_architecture.drawio', xml)

# ============================================================================
# DIAGRAM 2: Data Flow Pipeline
# ============================================================================
def create_data_flow():
    cells = [
        # Title
        {'id': 'title', 'value': 'Pipeline Xử Lý CT Volume → 3D Rendering', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '300', 'y': '20', 'width': '600', 'height': '40', 'as': 'geometry'}},
        
        # Pipeline steps
        {'id': 'step1', 'value': 'NIfTI File\n.nii/.nii.gz', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FF6B6B;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '100', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step2', 'value': 'Load Volume\n512×512×200', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#4ECDC4;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '200', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step3', 'value': 'HU Windowing\n-150 to 250 HU', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#45B7D1;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '300', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step4', 'value': 'Slice Extraction\n2D Images', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#96CEB4;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '280', 'y': '400', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step5', 'value': 'U-Net Pancreas\n256×256 Mask', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEAA7;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '280', 'y': '500', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step6', 'value': 'Loop Processing\nZ=0 to N', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#DFE6E9;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '720', 'y': '400', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step7', 'value': 'U-Net Tumor\n128×128 Mask', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEAA7;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '720', 'y': '500', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step8', 'value': '3D Mask Volume\n256×256×N', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#74B9FF;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '600', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step9', 'value': 'Marching Cubes\nMesh Generation', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#A29BFE;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '700', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step10', 'value': 'Mesh Processing\nSimplification', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FD79A8;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '280', 'y': '800', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step11', 'value': 'glTF Export\nBase64 Encode', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FDCB6E;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '720', 'y': '800', 'width': '160', 'height': '60', 'as': 'geometry'}},
        {'id': 'step12', 'value': '3D Viewer (WebGL)\nInteractive Render', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#00B894;strokeColor=#000000;strokeWidth=2;fontSize=11;fontStyle=1;fontColor=#FFFFFF;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '500', 'y': '900', 'width': '160', 'height': '60', 'as': 'geometry'}},
        
        # Arrows connecting steps
        {'id': 'arrow1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step1', 'target': 'step2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step2', 'target': 'step3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow3', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step3', 'target': 'step4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow4', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step3', 'target': 'step6', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow5', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step4', 'target': 'step5', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow6', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step6', 'target': 'step7', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow7', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step5', 'target': 'step8', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow8', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step7', 'target': 'step8', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow9', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step8', 'target': 'step9', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow10', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step9', 'target': 'step10', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow11', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step9', 'target': 'step11', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow12', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step10', 'target': 'step12', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow13', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step11', 'target': 'step12', 'geometry': {'relative': '1', 'as': 'geometry'}},
        
        # Timing annotations
        {'id': 'time1', 'value': '~200ms/slice', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontColor=#FF0000;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '420', 'width': '100', 'height': '30', 'as': 'geometry'}},
        {'id': 'time2', 'value': '~5-15s total', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontColor=#FF0000;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '620', 'width': '100', 'height': '30', 'as': 'geometry'}},
        {'id': 'time3', 'value': '~2-5s', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontColor=#FF0000;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '720', 'width': '100', 'height': '30', 'as': 'geometry'}},
    ]
    
    xml = create_drawio_xml('data-flow', 1200, 1000, cells)
    save_drawio('diagram_2_data_flow_pipeline.drawio', xml)

# ============================================================================
# DIAGRAM 3: Marching Cubes
# ============================================================================
def create_marching_cubes():
    cells = [
        # Title
        {'id': 'title', 'value': 'Thuật Toán Marching Cubes', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '300', 'y': '20', 'width': '600', 'height': '40', 'as': 'geometry'}},
        
        # Step boxes
        {'id': 'step1_title', 'value': 'Bước 1: Volume 3D', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '100', 'y': '100', 'width': '200', 'height': '30', 'as': 'geometry'}},
        {'id': 'step1_box', 'value': '256×256×N voxels', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1976D2;strokeWidth=2;fontSize=11;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '100', 'y': '140', 'width': '200', 'height': '120', 'as': 'geometry'}},
        
        {'id': 'step2_title', 'value': 'Bước 2: Chia Thành Khối', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '400', 'y': '100', 'width': '200', 'height': '30', 'as': 'geometry'}},
        {'id': 'step2_box', 'value': '8 đỉnh:\nTrong (xanh) / Ngoài (đỏ)', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#F57C00;strokeWidth=2;fontSize=11;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '400', 'y': '140', 'width': '200', 'height': '120', 'as': 'geometry'}},
        
        {'id': 'step3_title', 'value': 'Bước 3: Tạo Tam Giác', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '700', 'y': '100', 'width': '200', 'height': '30', 'as': 'geometry'}},
        {'id': 'step3_box', 'value': '2⁸ = 256 cấu hình', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F9A825;strokeWidth=2;fontSize=11;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '700', 'y': '140', 'width': '200', 'height': '120', 'as': 'geometry'}},
        
        # Process details
        {'id': 'process_title', 'value': 'Quy Trình Chi Tiết', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=15;fontStyle=1;fontColor=#2C3E50;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '100', 'y': '300', 'width': '800', 'height': '40', 'as': 'geometry'}},
        
        {'id': 'process', 'value': '1. Chia volume thành các ô khối 2×2×2 (8 đỉnh mỗi khối)\n2. Với mỗi đỉnh: kiểm tra giá trị > threshold (0.5) → đánh dấu trong/ngoài\n3. Tạo 8-bit index từ trạng thái 8 đỉnh (ví dụ: 10110100)\n4. Tra lookup table để lấy cấu hình tam giác tương ứng\n5. Nội suy vị trí đỉnh chính xác dọc theo cạnh khối\n6. Tạo vertices (tọa độ x,y,z) và faces (chỉ số 3 đỉnh)\n7. Tính normal vectors cho mỗi đỉnh (để lighting)\n8. Áp dụng spacing để chuyển từ voxel space → physical space (mm)', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=11;spacingLeft=20;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '100', 'y': '350', 'width': '800', 'height': '200', 'as': 'geometry'}},
        
        # Output box
        {'id': 'output_box', 'value': 'OUTPUT', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#4CAF50;strokeWidth=2;fontSize=13;fontStyle=1;align=center;verticalAlign=top;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '100', 'y': '600', 'width': '800', 'height': '120', 'as': 'geometry'}},
        
        {'id': 'output_text', 'value': 'Vertices: Mảng Mx3 (ví dụ: 50,000 × 3 = 150,000 giá trị)\nFaces: Mảng Kx3 (ví dụ: 100,000 × 3 = 300,000 chỉ số)\nNormals: Mảng Mx3 (vector pháp tuyến cho lighting)', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=10;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '150', 'y': '640', 'width': '700', 'height': '60', 'as': 'geometry'}},
        
        # Arrows
        {'id': 'arrow1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#000000;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step1_box', 'target': 'step2_box', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#000000;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step2_box', 'target': 'step3_box', 'geometry': {'relative': '1', 'as': 'geometry'}},
    ]
    
    xml = create_drawio_xml('marching-cubes', 1200, 800, cells)
    save_drawio('diagram_3_marching_cubes.drawio', xml)

# ============================================================================
# DIAGRAM 4: U-Net Architecture
# ============================================================================
def create_unet():
    cells = [
        # Title
        {'id': 'title', 'value': 'Kiến Trúc U-Net Cho Phân Đoạn', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '400', 'y': '20', 'width': '600', 'height': '40', 'as': 'geometry'}},
        
        # Input
        {'id': 'input', 'value': 'Input\n256×256×1', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#E8EAF6;strokeColor=#3F51B5;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '50', 'y': '200', 'width': '100', 'height': '100', 'as': 'geometry'}},
        
        # Encoder blocks
        {'id': 'enc1', 'value': '64\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#BBDEFB;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '200', 'y': '210', 'width': '80', 'height': '90', 'as': 'geometry'}},
        {'id': 'enc2', 'value': '128\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#90CAF9;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '330', 'y': '220', 'width': '70', 'height': '80', 'as': 'geometry'}},
        {'id': 'enc3', 'value': '256\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#64B5F6;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '450', 'y': '230', 'width': '60', 'height': '70', 'as': 'geometry'}},
        {'id': 'enc4', 'value': '512\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#42A5F5;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '560', 'y': '240', 'width': '50', 'height': '60', 'as': 'geometry'}},
        
        # Bottleneck
        {'id': 'bottleneck', 'value': '1024', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#1976D2;strokeColor=#0D47A1;strokeWidth=2;fontSize=10;fontStyle=1;fontColor=#FFFFFF;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '650', 'y': '250', 'width': '50', 'height': '50', 'as': 'geometry'}},
        
        # Decoder blocks
        {'id': 'dec1', 'value': '512\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#42A5F5;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '740', 'y': '240', 'width': '50', 'height': '60', 'as': 'geometry'}},
        {'id': 'dec2', 'value': '256\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#64B5F6;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '840', 'y': '230', 'width': '60', 'height': '70', 'as': 'geometry'}},
        {'id': 'dec3', 'value': '128\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#90CAF9;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '950', 'y': '220', 'width': '70', 'height': '80', 'as': 'geometry'}},
        {'id': 'dec4', 'value': '64\nfilters', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#BBDEFB;strokeColor=#1976D2;strokeWidth=2;fontSize=10;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '1070', 'y': '210', 'width': '80', 'height': '90', 'as': 'geometry'}},
        
        # Output
        {'id': 'output', 'value': 'Output\n256×256×1\nMask', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;strokeColor=#4CAF50;strokeWidth=2;fontSize=11;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '1200', 'y': '200', 'width': '100', 'height': '100', 'as': 'geometry'}},
        
        # Skip connections (dashed arrows)
        {'id': 'skip1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#FF6F00;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'enc1', 'target': 'dec4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'skip2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#FF6F00;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'enc2', 'target': 'dec3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'skip3', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#FF6F00;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'enc3', 'target': 'dec2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        
        {'id': 'skip_label', 'value': 'Skip Connections', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;fontStyle=3;fontColor=#FF6F00;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '550', 'y': '150', 'width': '150', 'height': '30', 'as': 'geometry'}},
        
        # Sequential arrows
        {'id': 'arrow1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#000000;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'input', 'target': 'enc1', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow2', 'value': '2×2 pool', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#D32F2F;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'enc1', 'target': 'enc2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow3', 'value': '2×2 pool', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#D32F2F;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'enc2', 'target': 'enc3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow4', 'value': '2×2 pool', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#D32F2F;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'enc3', 'target': 'enc4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow5', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#D32F2F;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'enc4', 'target': 'bottleneck', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow6', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#388E3C;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'bottleneck', 'target': 'dec1', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow7', 'value': '2×2 up', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#388E3C;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'dec1', 'target': 'dec2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow8', 'value': '2×2 up', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#388E3C;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'dec2', 'target': 'dec3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow9', 'value': '2×2 up', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#388E3C;endArrow=classic;endFill=1;fontSize=8;', 'edge': '1', 'parent': '1', 'source': 'dec3', 'target': 'dec4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow10', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;strokeColor=#000000;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'dec4', 'target': 'output', 'geometry': {'relative': '1', 'as': 'geometry'}},
        
        # Labels
        {'id': 'label_encoder', 'value': 'Encoder (Downsampling)', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontStyle=1;fontColor=#D32F2F;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '300', 'y': '350', 'width': '200', 'height': '30', 'as': 'geometry'}},
        {'id': 'label_bottleneck', 'value': 'Bottleneck', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '625', 'y': '350', 'width': '100', 'height': '30', 'as': 'geometry'}},
        {'id': 'label_decoder', 'value': 'Decoder (Upsampling)', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontStyle=1;fontColor=#388E3C;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '850', 'y': '350', 'width': '200', 'height': '30', 'as': 'geometry'}},
    ]
    
    xml = create_drawio_xml('unet', 1400, 500, cells)
    save_drawio('diagram_4_unet_architecture.drawio', xml)

# ============================================================================
# DIAGRAM 5: WebGL Pipeline
# ============================================================================
def create_webgl_pipeline():
    cells = [
        # Title
        {'id': 'title', 'value': 'Pipeline WebGL Rendering', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '200', 'y': '20', 'width': '600', 'height': '40', 'as': 'geometry'}},
        
        # Pipeline steps
        {'id': 'step1', 'value': 'glTF Binary Data\n(Base64 Decoded)', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FF6B6B;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '100', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step2', 'value': 'Parse glTF Structure\nVertices, Faces, Materials', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#4ECDC4;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '220', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step3', 'value': 'Create WebGL Buffers\nVertex Buffer, Index Buffer', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#45B7D1;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '340', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step4', 'value': 'Compile Shaders\nVertex + Fragment Shaders', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#96CEB4;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '460', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step5', 'value': 'Setup Scene\nCamera, Lights, Materials', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEAA7;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '580', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step6', 'value': 'Render Loop (60 FPS)\nDraw Calls + User Input', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#74B9FF;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '700', 'width': '300', 'height': '80', 'as': 'geometry'}},
        {'id': 'step7', 'value': '3D Interactive View\nRotate, Zoom, Pan', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#00B894;strokeColor=#000000;strokeWidth=2;fontSize=12;fontStyle=1;fontColor=#FFFFFF;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '350', 'y': '820', 'width': '300', 'height': '80', 'as': 'geometry'}},
        
        # Annotations
        {'id': 'anno1', 'value': 'Flutter 3D\nController', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '120', 'width': '100', 'height': '40', 'as': 'geometry'}},
        {'id': 'anno2', 'value': 'JSON\nParsing', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '240', 'width': '100', 'height': '40', 'as': 'geometry'}},
        {'id': 'anno3', 'value': 'WebGL\nContext', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '360', 'width': '100', 'height': '40', 'as': 'geometry'}},
        {'id': 'anno4', 'value': 'GLSL\nCode', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '480', 'width': '100', 'height': '40', 'as': 'geometry'}},
        {'id': 'anno5', 'value': '3D Math\nLibraries', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '600', 'width': '100', 'height': '40', 'as': 'geometry'}},
        {'id': 'anno6', 'value': 'Event\nHandlers', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=10;fontStyle=2;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '730', 'y': '720', 'width': '100', 'height': '40', 'as': 'geometry'}},
        
        # Performance metrics box
        {'id': 'metrics_box', 'value': 'Hiệu Suất', 'style': 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3CD;strokeColor=#856404;strokeWidth=2;fontSize=12;fontStyle=1;align=center;verticalAlign=top;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '70', 'y': '400', 'width': '200', 'height': '150', 'as': 'geometry'}},
        {'id': 'metrics_text', 'value': 'FPS: 60\nVertices: 15K\nTriangles: 15K\nDraw Calls: 2\nMemory: ~50MB', 'style': 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=10;', 'vertex': '1', 'parent': '1', 'geometry': {'x': '80', 'y': '440', 'width': '180', 'height': '100', 'as': 'geometry'}},
        
        # Arrows
        {'id': 'arrow1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step1', 'target': 'step2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step2', 'target': 'step3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow3', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step3', 'target': 'step4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow4', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step4', 'target': 'step5', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow5', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step5', 'target': 'step6', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow6', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=3;strokeColor=#2C3E50;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step6', 'target': 'step7', 'geometry': {'relative': '1', 'as': 'geometry'}},
        
        # Annotation arrows
        {'id': 'arrow_a1', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step1', 'target': 'anno1', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow_a2', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step2', 'target': 'anno2', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow_a3', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step3', 'target': 'anno3', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow_a4', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step4', 'target': 'anno4', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow_a5', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step5', 'target': 'anno5', 'geometry': {'relative': '1', 'as': 'geometry'}},
        {'id': 'arrow_a6', 'value': '', 'style': 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;dashed=1;endArrow=classic;endFill=1;', 'edge': '1', 'parent': '1', 'source': 'step6', 'target': 'anno6', 'geometry': {'relative': '1', 'as': 'geometry'}},
    ]
    
    xml = create_drawio_xml('webgl', 1000, 1000, cells)
    save_drawio('diagram_5_webgl_pipeline.drawio', xml)

# ============================================================================
# Main execution
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("Tạo Draw.io Diagrams Cho Tài Liệu 3D Viewer")
    print("="*70 + "\n")
    
    create_system_architecture()
    create_data_flow()
    create_marching_cubes()
    create_unet()
    create_webgl_pipeline()
    
    print("\n" + "="*70)
    print("✓ Hoàn Tất! Tất cả diagrams đã được tạo:")
    print("  1. diagram_1_system_architecture.drawio")
    print("  2. diagram_2_data_flow_pipeline.drawio")
    print("  3. diagram_3_marching_cubes.drawio")
    print("  4. diagram_4_unet_architecture.drawio")
    print("  5. diagram_5_webgl_pipeline.drawio")
    print("\nMở các file .drawio trong VS Code hoặc app.diagrams.net để chỉnh sửa!")
    print("="*70 + "\n")
