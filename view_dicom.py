import pydicom
import matplotlib.pyplot as plt
import sys
import os

def show_dicom_image(ds):
    img = ds.pixel_array

    # Handle multi-frame images by selecting the first frame
    if img.ndim == 4:
        print(f"Multi-frame image detected. Shape: {img.shape}")
        img = img[0]

    plt.imshow(img, cmap='gray' if img.ndim == 2 else None)
    plt.title(f"Modality: {getattr(ds, 'Modality', 'Unknown')}, Patient ID: {getattr(ds, 'PatientID', 'Unknown')}")
    plt.axis('off')
    plt.show()

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
        print(f"\nDisplaying: {filename}")
        ds = pydicom.dcmread(full_path)
        show_dicom_image(ds)
        input("Press Enter to continue to the next image...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_dicom.py <directory_with_dicom_files>")
        sys.exit(1)
    
    dicom_dir = sys.argv[1]
    if not os.path.isdir(dicom_dir):
        print(f"Error: {dicom_dir} is not a valid directory.")
        sys.exit(1)

    load_and_display_all_dicoms(dicom_dir)