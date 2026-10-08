import os
import zipfile
import urllib.request
import shutil

def download_high_feature_dataset():
    print("==================================================")
    print(" DOWNLOADING TEXTURE-AWARE RESTRICTED OBJECT DATASET ")
    print("==================================================")

    # Annotated Weapons & Sharp Objects dataset zip archive
    dataset_url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco8.zip"
    zip_save_path = "dataset_textures.zip"

    print("Downloading high-resolution annotated samples...")
    urllib.request.urlretrieve(dataset_url, zip_save_path)

    target_dir = os.path.abspath("dataset")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    with zipfile.ZipFile(zip_save_path, 'r') as zip_ref:
        zip_ref.extractall("temp_dataset")

    extracted_folder = os.path.join("temp_dataset", os.listdir("temp_dataset")[0])
    shutil.move(extracted_folder, target_dir)

    if os.path.exists(zip_save_path):
        os.remove(zip_save_path)
    if os.path.exists("temp_dataset"):
        shutil.rmtree("temp_dataset")

    print("\nDataset ready inside 'dataset/' folder!")

if __name__ == "__main__":
    download_high_feature_dataset()