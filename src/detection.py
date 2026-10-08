import os
import cv2
from datetime import datetime
from ultralytics import YOLO

def detect_and_count_image(image_path, model_path="yolov8n.pt", conf_threshold=0.25):
    """
    Performs object detection, classification, and counting on a single image.
    
    Args:
        image_path (str): Path to input image file.
        model_path (str): Path to trained YOLO model weights.
        conf_threshold (float): Minimum confidence threshold for detection.
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] Image path does not exist: {image_path}")
        return

    print(f"Loading YOLO model from: {model_path}...")
    model = YOLO(model_path)

    # Read image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Could not read image at: {image_path}")
        return

    print(f"Running object detection on: {image_path}...")
    # Perform inference
    results = model(img, conf=conf_threshold)[0]

    # Initialize detection and counting dictionary
    class_counts = {}
    detection_logs = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Parse detection boxes
    boxes = results.boxes
    total_detected = len(boxes)

    for box in boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        confidence = float(box.conf[0]) * 100

        # Update class object counts
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Store record metadata
        detection_logs.append({
            "Timestamp": timestamp,
            "Category": class_name,
            "Confidence": f"{confidence:.2f}%"
        })

    # Render bounding boxes onto image using Ultralytics plot utility
    annotated_frame = results.plot()

    # Save output visualization
    os.makedirs("results", exist_ok=True)
    output_filename = f"detected_{os.path.basename(image_path)}"
    output_save_path = os.path.join("results", output_filename)
    cv2.imwrite(output_save_path, annotated_frame)

    # Display structured detection summary in console
    print("\n==================================================")
    print("           DETECTION & COUNTING LOG               ")
    print("==================================================")
    print(f" Timestamp       : {timestamp}")
    print(f" Total Detected  : {total_detected}")
    print(" Class Breakdown :")
    for category, count in class_counts.items():
        print(f"   - {category:<15} : {count}")
    print("--------------------------------------------------")
    print(f" Output Image Saved to : {output_save_path}")
    print("==================================================\n")

    return detection_logs

if __name__ == "__main__":
    # Test on local sample image generated in dataset
    sample_img = os.path.abspath("dataset/images/train/sample1.jpg")
    detect_and_count_image(sample_img, model_path="yolov8n.pt")