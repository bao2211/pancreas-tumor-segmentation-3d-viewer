import gradio as gr
import pandas as pd
import numpy as np
from PIL import Image
import os

# Default base directory
DEFAULT_BASE_DIR = r"i:\My Drive\Colab Notebooks\DATA_Pancreas_Segmentation_Bao_fix"


def load_csv(base_dir, csv_name):
    """Load CSV and return list of unique patient IDs"""
    if not base_dir or not csv_name:
        return []
    csv_path = os.path.join(base_dir, "csv_files", f"{csv_name}.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        patient_ids = sorted(df['patient_id'].unique().tolist())
        return patient_ids
    return []


def normalize_array(arr):
    """Normalize array to 0-255 range for image saving"""
    arr = arr.astype(np.float32)
    if arr.max() > arr.min():
        arr = (arr - arr.min()) / (arr.max() - arr.min()) * 255
    return arr.astype(np.uint8)


def create_combined_image(image_arr, label_arr):
    """Create combined image with label overlay in red"""
    # Normalize image to 0-255
    img_normalized = normalize_array(image_arr)
    
    # Create RGB image from grayscale
    rgb_image = np.stack([img_normalized, img_normalized, img_normalized], axis=-1)
    
    # Create red overlay for label (where label > 0)
    label_mask = label_arr > 0
    rgb_image[label_mask, 0] = np.minimum(rgb_image[label_mask, 0].astype(np.int32) + 100, 255).astype(np.uint8)  # Red
    rgb_image[label_mask, 1] = (rgb_image[label_mask, 1] * 0.5).astype(np.uint8)  # Reduce green
    rgb_image[label_mask, 2] = (rgb_image[label_mask, 2] * 0.5).astype(np.uint8)  # Reduce blue
    
    return rgb_image


def convert_npy_to_png(base_dir, csv_name, patient_id):
    """Convert all NPY files for a patient to PNG"""
    if not base_dir:
        return "Please enter a base directory path."
    if not csv_name:
        return "Please select a CSV file."
    if not patient_id:
        return "Please select or enter a patient ID."
    
    # Clean inputs
    base_dir = base_dir.strip()
    patient_id = patient_id.strip()
    
    # Set up paths
    csv_dir = os.path.join(base_dir, "csv_files")
    image_dir = os.path.join(base_dir, "image")
    label_dir = os.path.join(base_dir, "label")
    
    # Output directories (inside app folder)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    output_base = os.path.join(app_dir, "png_output")
    output_image_only = os.path.join(output_base, "image_only")
    output_label_only = os.path.join(output_base, "label_only")
    output_combined = os.path.join(output_base, "combined")
    
    # Load CSV
    csv_path = os.path.join(csv_dir, f"{csv_name}.csv")
    if not os.path.exists(csv_path):
        return f"CSV file not found: {csv_path}"
    
    df = pd.read_csv(csv_path)
    
    # Filter for the specific patient
    patient_df = df[df['patient_id'] == patient_id]
    
    if patient_df.empty:
        return f"Patient ID '{patient_id}' not found in {csv_name}.csv"
    
    # Create output directories
    patient_image_dir = os.path.join(output_image_only, patient_id)
    patient_label_dir = os.path.join(output_label_only, patient_id)
    patient_combined_dir = os.path.join(output_combined, patient_id)
    
    os.makedirs(patient_image_dir, exist_ok=True)
    os.makedirs(patient_label_dir, exist_ok=True)
    os.makedirs(patient_combined_dir, exist_ok=True)
    
    converted_count = 0
    errors = []
    
    for _, row in patient_df.iterrows():
        # Get local paths (convert from Colab paths to local paths)
        image_filename = os.path.basename(row['image_path'])
        label_filename = os.path.basename(row['label_path'])
        
        image_path = os.path.join(image_dir, image_filename)
        label_path = os.path.join(label_dir, label_filename)
        
        # Check if files exist
        if not os.path.exists(image_path):
            errors.append(f"Image not found: {image_filename}")
            continue
        if not os.path.exists(label_path):
            errors.append(f"Label not found: {label_filename}")
            continue
        
        try:
            # Load NPY files
            image_arr = np.load(image_path)
            label_arr = np.load(label_path)
            
            # Get base name for output
            base_name = image_filename.replace('.npy', '.png')
            
            # Save image only
            img_normalized = normalize_array(image_arr)
            img_pil = Image.fromarray(img_normalized, mode='L')
            img_pil.save(os.path.join(patient_image_dir, base_name))
            
            # Save label only (binary mask scaled to 255)
            label_normalized = (label_arr > 0).astype(np.uint8) * 255
            label_pil = Image.fromarray(label_normalized, mode='L')
            label_pil.save(os.path.join(patient_label_dir, base_name))
            
            # Save combined
            combined_arr = create_combined_image(image_arr, label_arr)
            combined_pil = Image.fromarray(combined_arr, mode='RGB')
            combined_pil.save(os.path.join(patient_combined_dir, base_name))
            
            converted_count += 1
            
        except Exception as e:
            errors.append(f"Error processing {image_filename}: {str(e)}")
    
    # Build result message
    result = f"✅ Converted {converted_count} slices for patient '{patient_id}'\n\n"
    result += f"📁 Output directories:\n"
    result += f"   • Image only: {patient_image_dir}\n"
    result += f"   • Label only: {patient_label_dir}\n"
    result += f"   • Combined: {patient_combined_dir}\n"
    
    if errors:
        result += f"\n⚠️ Errors ({len(errors)}):\n"
        for err in errors[:5]:  # Show max 5 errors
            result += f"   • {err}\n"
        if len(errors) > 5:
            result += f"   ... and {len(errors) - 5} more errors\n"
    
    return result


def update_patient_list(base_dir, csv_name):
    """Update patient ID suggestions based on selected CSV"""
    if base_dir and csv_name:
        patients = load_csv(base_dir, csv_name)
        return gr.update(choices=patients, value=None)
    return gr.update(choices=[], value=None)


def validate_base_dir(base_dir):
    """Validate the base directory and return status"""
    if not base_dir:
        return "⚠️ Please enter a base directory path"
    
    base_dir = base_dir.strip()
    
    if not os.path.exists(base_dir):
        return f"❌ Directory not found: {base_dir}"
    
    # Check for required subdirectories
    csv_dir = os.path.join(base_dir, "csv_files")
    image_dir = os.path.join(base_dir, "image")
    label_dir = os.path.join(base_dir, "label")
    
    missing = []
    if not os.path.exists(csv_dir):
        missing.append("csv_files")
    if not os.path.exists(image_dir):
        missing.append("image")
    if not os.path.exists(label_dir):
        missing.append("label")
    
    if missing:
        return f"❌ Missing subdirectories: {', '.join(missing)}"
    
    # Check for CSV files
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    return f"✅ Valid directory! Found {len(csv_files)} CSV file(s)"


# Create Gradio interface
with gr.Blocks(title="NPY to PNG Converter") as app:
    gr.Markdown("# 🔄 NPY to PNG Converter")
    gr.Markdown("Convert NPY slice files to PNG images for visualization.")
    
    with gr.Row():
        with gr.Column():
            base_dir_input = gr.Textbox(
                value=DEFAULT_BASE_DIR,
                label="Base Directory Path",
                info="Path to the folder containing csv_files, image, and label directories",
                placeholder="Enter the base directory path..."
            )
            
            base_dir_status = gr.Textbox(
                label="Directory Status",
                interactive=False,
                lines=1
            )
            
            csv_dropdown = gr.Dropdown(
                choices=["train", "test", "valid"],
                label="Select CSV File",
                info="Choose which dataset to use"
            )
            
            patient_input = gr.Dropdown(
                choices=[],
                label="Patient ID",
                info="Select or type a patient ID (e.g., pancreas_278)",
                allow_custom_value=True
            )
            
            convert_btn = gr.Button("🔄 Convert to PNG", variant="primary")
    
    output_text = gr.Textbox(
        label="Result",
        lines=12,
        interactive=False
    )
    
    # Event handlers
    base_dir_input.change(
        fn=validate_base_dir,
        inputs=[base_dir_input],
        outputs=[base_dir_status]
    )
    
    # Update patient list when base_dir or csv changes
    base_dir_input.change(
        fn=update_patient_list,
        inputs=[base_dir_input, csv_dropdown],
        outputs=[patient_input]
    )
    
    csv_dropdown.change(
        fn=update_patient_list,
        inputs=[base_dir_input, csv_dropdown],
        outputs=[patient_input]
    )
    
    convert_btn.click(
        fn=convert_npy_to_png,
        inputs=[base_dir_input, csv_dropdown, patient_input],
        outputs=[output_text]
    )
    
    # Validate on load
    app.load(
        fn=validate_base_dir,
        inputs=[base_dir_input],
        outputs=[base_dir_status]
    )


if __name__ == "__main__":
    app.launch()
