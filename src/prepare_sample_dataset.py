import os
import urllib.request

def prepare():
    # Ensure dataset directories exist
    os.makedirs('dataset/images/train', exist_ok=True)
    os.makedirs('dataset/images/val', exist_ok=True)
    os.makedirs('dataset/labels/train', exist_ok=True)
    os.makedirs('dataset/labels/val', exist_ok=True)

    # Sample test image URL
    sample_img_url = 'https://ultralytics.com/images/bus.jpg'

    print('Downloading sample image for train/val split test...')
    urllib.request.urlretrieve(sample_img_url, 'dataset/images/train/sample1.jpg')
    urllib.request.urlretrieve(sample_img_url, 'dataset/images/val/sample1.jpg')

    # Standard YOLO label format: <class_id> <x_center> <y_center> <width> <height>
    sample_label = '0 0.5 0.5 0.3 0.4\n'

    with open('dataset/labels/train/sample1.txt', 'w') as f:
        f.write(sample_label)

    with open('dataset/labels/val/sample1.txt', 'w') as f:
        f.write(sample_label)

    print('Sample dataset setup successfully!')

if __name__ == "__main__":
    prepare()