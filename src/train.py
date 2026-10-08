import os
from ultralytics import YOLO

def train_ultra_efficient_model():
    print("==================================================")
    print("  TRAINING ULTRA-EFFICIENT MULTI-OBJECT DETECTOR   ")
    print("==================================================")

    model = YOLO("yolov8s.pt")
    yaml_path = os.path.abspath("dataset/data.yaml")

    print(f"\n[INFO] Loading dataset config: {yaml_path}")
    
    # Fine-tune model with heavy data augmentations for sharp accuracy
    results = model.train(
        data=yaml_path,
        epochs=20,               # 20 Epochs fine-tuning
        imgsz=640,               # Full 640x640 sharp resolution
        batch=2,
        hsv_h=0.015,             # Color jitter
        hsv_s=0.7,               # Saturation adjustment
        hsv_v=0.4,               # Contrast/Brightness variation
        degrees=15.0,            # Rotation invariance
        translate=0.1,           # Positional invariance
        scale=0.5,               # Multi-scale zoom
        mosaic=1.0,              # Mosaic feature stitching
        project="runs/detect",
        name="ultra_efficient_model",
        exist_ok=True
    )

    best_weights = os.path.abspath("runs/detect/ultra_efficient_model/weights/best.pt")
    print(f"\n✅ Training Completed! High-Accuracy Weights: {best_weights}")

if __name__ == "__main__":
    train_ultra_efficient_model()