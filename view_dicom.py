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

def load_and_display_all_dicoms(root_dir):
    for dirpath, _, files in os.walk(root_dir):
        dicom_files = sorted([f for f in files if f.lower().endswith('.dcm')])
        
        for filename in dicom_files:
            full_path = os.path.join(dirpath, filename)
            print(f"\n📄 Displaying: {full_path}")

            ds = pydicom.dcmread(full_path)

            json_filename = os.path.splitext(filename)[0] + '.json'
            json_path = os.path.join(dirpath, json_filename)

            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)

                    if data.get("mask_type") == "rectangle":
                        print("🚫 Skipping due to rectangular mask")
                        continue

                    inner_radius = data.get("radius1", None)

                    show_dicom_image(ds, filename)

                    if inner_radius is None:
                        print("⚠️  radius1 not found in JSON.")
                        plt.close()
                        continue

                    if 5 < inner_radius < 10:
                        print(f"🤔 radius1 = {inner_radius}, please decide:")
                        user_input = input("Enter 'p' for phased-array or 'c' for curvilinear: ").strip().lower()
                        label = "phased-array" if user_input == 'p' else "curvilinear"
                    else:
                        label = "phased-array" if inner_radius <= 5 else "curvilinear"
                        print(f"🔍 Detected probe type: {label} (radius1 = {inner_radius})")

                    if "Annotation Labels" not in data or not isinstance(data["Annotation Labels"], list) or not data["Annotation Labels"]:
                        data["Annotation Labels"] = [label]
                    else:
                        existing_label = data["Annotation Labels"][0]
                        if label not in existing_label:
                            data["Annotation Labels"][0] = f"{existing_label} | {label}"

                    with open(json_path, 'w') as f:
                        json.dump(data, f, indent=4)

                    print("\n📋 Updated JSON metadata:")
                    print(json.dumps(data, indent=4))

                    plt.close()

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
