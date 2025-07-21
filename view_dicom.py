import matplotlib
matplotlib.rcParams['toolbar'] = 'none'

import pydicom
import matplotlib.pyplot as plt
import sys
import os
import json

def show_dicom_image(ds, filename):
    img = ds.pixel_array

    # Handle multi-frame images by selecting the first frame
    if img.ndim == 4:
        print(f"Multi-frame image detected. Shape: {img.shape}")
        img = img[0]

    modality = getattr(ds, 'Modality', 'Unknown')
    plt.imshow(img, cmap='gray' if img.ndim == 2 else None)
    plt.title(f"{filename} — Modality: {modality}")
    plt.axis('off')
    plt.show(block=False)
    input("Press Enter to continue to the next image...")
    plt.close()

def load_and_display_all_dicoms(directory_path):
    # Get all .dcm files
    dicom_files = sorted([
        f for f in os.listdir(directory_path)
        if f.lower().endswith('.dcm')
    ])

    if not dicom_files:
        print("No DICOM files found in the directory.")
        return

    for filename in dicom_files:
        full_path = os.path.join(directory_path, filename)
        print(f"\n📄 Displaying: {filename}")

        # Read DICOM file
        ds = pydicom.dcmread(full_path)

        # Load and pretty-print matching JSON
        json_filename = os.path.splitext(filename)[0] + '.json'
        json_path = os.path.join(directory_path, json_filename)

        if os.path.exists(json_path):
            print("📋 Associated JSON metadata:")
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=4))
            except json.JSONDecodeError:
                print(f"⚠️  Warning: Could not parse JSON file: {json_filename}")
        else:
            print(f"⚠️  No matching JSON file found: {json_filename}")

        # Show image and wait for user
        show_dicom_image(ds, filename)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_dicom.py <directory_with_dicom_files>")
        sys.exit(1)
    
    dicom_dir = sys.argv[1]
    if not os.path.isdir(dicom_dir):
        print(f"Error: {dicom_dir} is not a valid directory.")
        sys.exit(1)

    load_and_display_all_dicoms(dicom_dir)