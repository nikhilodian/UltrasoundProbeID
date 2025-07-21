import pydicom
import matplotlib.pyplot as plt
import sys

def show_dicom_image(dicom_path):
    ds = pydicom.dcmread(dicom_path)
    img = ds.pixel_array

    # Handle multi-frame images by selecting the first frame
    if img.ndim == 4:
        print(f"Multi-frame image detected. Shape: {img.shape}")
        img = img[0]  # Take the first frame: (920, 1590, 3)

    plt.imshow(img, cmap='gray' if img.ndim == 2 else None)
    plt.title(f"Modality: {ds.Modality}, Patient ID: {ds.PatientID}")
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_dicom.py <path_to_dicom_file>")
        sys.exit(1)
    show_dicom_image(sys.argv[1])