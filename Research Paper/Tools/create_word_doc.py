"""
Create a basic Word document using python-docx library
"""
from docx import Document
from docx.shared import Inches

# Create a new Document
document = Document()

# Add a title
document.add_heading('Sample Word Document', 0)

# Add a paragraph with plain text
document.add_paragraph('This is a basic Word document created using python-docx library.')

# Add a heading
document.add_heading('Introduction', level=1)

# Add a paragraph with styled text
p = document.add_paragraph('This document demonstrates how to create a ')
p.add_run('Word file').bold = True
p.add_run(' programmatically using Python.')

# Add another heading
document.add_heading('Features', level=1)

# Add bullet list
document.add_paragraph('Easy to use', style='List Bullet')
document.add_paragraph('Supports text formatting', style='List Bullet')
document.add_paragraph('Can add tables and images', style='List Bullet')

# Add a numbered list
document.add_heading('Steps', level=1)
document.add_paragraph('Install python-docx', style='List Number')
document.add_paragraph('Import the Document class', style='List Number')
document.add_paragraph('Create and save your document', style='List Number')

# Add a simple table
document.add_heading('Sample Table', level=1)
table = document.add_table(rows=3, cols=3)
table.style = 'Light Grid Accent 1'

# Add headers
header_cells = table.rows[0].cells
header_cells[0].text = 'Name'
header_cells[1].text = 'Age'
header_cells[2].text = 'City'

# Add data
row1 = table.rows[1].cells
row1[0].text = 'John Doe'
row1[1].text = '30'
row1[2].text = 'New York'

row2 = table.rows[2].cells
row2[0].text = 'Jane Smith'
row2[1].text = '25'
row2[2].text = 'Los Angeles'

# Save the document
output_file = 'basic_document.docx'
document.save(output_file)
print(f"Word document created successfully: {output_file}")
