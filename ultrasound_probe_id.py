import matplotlib
matplotlib.rcParams['toolbar'] = 'none'

import pydicom
import matplotlib.pyplot as plt
import sys
import os
import json

def show_dicom_image(ds, filename):
    img = ds.pixel_array

    if img.ndim == 4:
        print(f"Multi-frame image detected. Shape: {img.shape}")
        img = img[0]

    modality = getattr(ds, 'Modality', 'Unknown')
    plt.imshow(img, cmap='gray' if img.ndim == 2 else None)
    plt.title(f"{filename} — Modality: {modality}")
    plt.axis('off')
    plt.show(block=True)
    plt.close()

def load_and_display_all_dicoms(directory_path):
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

        ds = pydicom.dcmread(full_path)

        # Match and process corresponding JSON
        json_filename = os.path.splitext(filename)[0] + '.json'
        json_path = os.path.join(directory_path, json_filename)

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)

                # Show the image first
                show_dicom_image(ds, filename)

                # Determine label
                mask_type = data.get("mask_type")
                if mask_type == "rectangle":
                    label = "rectangle"
                    print("🟫 Detected rectangular mask, adding 'rectangle' label")
                else:
                    inner_radius = data.get("radius1", None)
                    if inner_radius is None:
                        print("⚠️  radius1 not found in JSON.")
                        continue

                    if 5 < inner_radius < 10:
                        print(f"🤔 radius1 = {inner_radius}, please decide:")
                        user_input = input("Enter 'p' for phased-array or 'c' for curvilinear: ").strip().lower()
                        label = "phased-array" if user_input == 'p' else "curvilinear"
                    else:
                        label = "phased-array" if inner_radius <= 5 else "curvilinear"
                        print(f"🔍 Detected probe type: {label} (radius1 = {inner_radius})")

                # Update Annotation Labels: append if not already in list
                if "Annotation Labels" not in data or not isinstance(data["Annotation Labels"], list):
                    data["Annotation Labels"] = [label]
                elif label not in data["Annotation Labels"]:
                    data["Annotation Labels"].append(label)

                # Save updated dictionary to file
                with open(json_path, 'w') as f:
                    json.dump(data, f, indent=4)

                # Show updated JSON
                print("\n📋 Updated JSON metadata:")
                print(json.dumps(data, indent=4))

            except json.JSONDecodeError:
                print(f"⚠️  Warning: Could not parse JSON file: {json_filename}")
        else:
            print(f"⚠️  No matching JSON file found: {json_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_dicom.py <directory_with_dicom_files>")
        sys.exit(1)

    dicom_dir = sys.argv[1]
    if not os.path.isdir(dicom_dir):
        print(f"Error: {dicom_dir} is not a valid directory.")
        sys.exit(1)

    load_and_display_all_dicoms(dicom_dir)
