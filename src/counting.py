import os
import sys
import cv2
import winsound
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLOWorld

# Resolve parent directory imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import init_db, log_detection_to_db, get_restricted_categories
from alerts import send_email_alert

# Async thread executor for smooth video FPS during email dispatch
alert_executor = ThreadPoolExecutor(max_workers=2)

def process_video_or_webcam(source=0, conf_threshold=0.32):
    init_db()
    
    print("[INFO] Loading Fine-Grained Multi-Prompt YOLO-World Engine...")
    model = YOLOWorld("yolov8s-world.pt")

    # Comprehensive descriptive prompts covering all variations
    custom_objects = [
        # Pencils & Writing Instruments
        "lead pencil", "sharpened wooden pencil", "graphite pencil", "mechanical pencil", 
        "ballpoint pen", "ink pen", "marker pen",
        
        # Grooming & Accessories
        "hair comb", "plastic hair comb", "black comb", "wrist watch", "smartwatch",
        
        # Identity & Cards
        "identity card", "plastic id card", "laminated identity badge", "atm card", "credit card",
        
        # Tools & Sharp Items (Restricted threats)
        "sharp knife blade", "kitchen knife", "folding pocket knife", "metal scissors", "cutting scissors",
        
        # Office & Daily Essentials
        "metal keys", "keychain ring", "leather wallet", "cell phone", "smartphone",
        "plastic water bottle", "drink cup", "coffee mug", "eyeglasses", "spectacles",
        "paper notebook", "open book", "usb flash drive", "computer mouse", "keyboard", "person"
    ]

    # Clean display mapping for screen labels, SQLite logs, and Email Alerts
    display_names = {
        "lead pencil": "pencil",
        "sharpened wooden pencil": "pencil",
        "graphite pencil": "pencil",
        "mechanical pencil": "pencil",
        "ballpoint pen": "pen",
        "ink pen": "pen",
        "marker pen": "pen",
        "hair comb": "comb",
        "plastic hair comb": "comb",
        "black comb": "comb",
        "wrist watch": "watch",
        "smartwatch": "watch",
        "identity card": "id card",
        "plastic id card": "id card",
        "laminated identity badge": "id card",
        "atm card": "card",
        "credit card": "card",
        "sharp knife blade": "knife",
        "kitchen knife": "knife",
        "folding pocket knife": "knife",
        "metal scissors": "scissors",
        "cutting scissors": "scissors",
        "metal keys": "keys",
        "keychain ring": "keys",
        "leather wallet": "wallet",
        "cell phone": "cell phone",
        "smartphone": "cell phone",
        "plastic water bottle": "bottle",
        "drink cup": "cup",
        "coffee mug": "cup",
        "eyeglasses": "spectacles",
        "spectacles": "spectacles",
        "paper notebook": "notebook",
        "open book": "notebook",
        "usb flash drive": "usb drive",
        "computer mouse": "mouse",
        "keyboard": "keyboard",
        "person": "person"
    }
    
    print(f"[INFO] Initializing {len(custom_objects)} fine-grained detection prompts...")
    model.set_classes(custom_objects)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open webcam: {source}")
        return

    # Set 720p HD resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    unique_tracked_ids = set()
    alerted_track_ids = set()
    detection_history = {}

    print("\n==================================================")
    print(" ALL-VARIATION ZERO-SHOT SECURITY MONITOR ACTIVE   ")
    print(" Detecting Lead Pencils, ID Cards, Combs & More!   ")
    print(" Press 'q' key in video window to exit.           ")
    print("==================================================\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        restricted_list = get_restricted_categories()
        has_active_restricted_threat = False

        # Run inference across all fine-grained text prompts
        results = model.predict(frame, conf=conf_threshold, verbose=False)[0]

        if results.boxes is not None and len(results.boxes) > 0:
            boxes_xyxy = results.boxes.xyxy.cpu().numpy()
            class_ids = results.boxes.cls.int().cpu().tolist()
            confidences = results.boxes.conf.cpu().tolist()

            for idx, (box, class_id, conf) in enumerate(zip(boxes_xyxy, class_ids, confidences)):
                raw_prompt = custom_objects[class_id] if class_id < len(custom_objects) else "unknown"
                class_name = display_names.get(raw_prompt, raw_prompt).lower()
                
                # Grid spatial key for persistent object verification
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                grid_key = f"{class_name}_{x1//35}_{y1//35}"

                detection_history[grid_key] = detection_history.get(grid_key, 0) + 1
                
                # Render detection if verified
                if detection_history[grid_key] >= 1:
                    is_restricted = 1 if class_name in restricted_list else 0
                    color = (0, 0, 255) if is_restricted else (0, 255, 0)

                    # Bounding Box & Clean Name Label
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{class_name.upper()} {conf*100:.1f}%", 
                                (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                    if is_restricted:
                        has_active_restricted_threat = True
                        if grid_key not in alerted_track_ids:
                            alerted_track_ids.add(grid_key)
                            alert_executor.submit(send_email_alert, class_name, conf * 100, frame.copy())

                    # Log to SQLite
                    if grid_key not in unique_tracked_ids:
                        unique_tracked_ids.add(grid_key)
                        alert_executor.submit(log_detection_to_db, len(unique_tracked_ids), class_name, conf * 100, is_restricted)

        # Alarm Sound & Red Warning Banner for Restricted Items
        if has_active_restricted_threat:
            winsound.Beep(2000, 50)
            cv2.rectangle(frame, (0, 0), (1280, 720), (0, 0, 255), 6)
            cv2.putText(frame, "⚠️ RESTRICTED THREAT DETECTED", (350, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # On-Screen HUD Overlay
        cv2.rectangle(frame, (10, 10), (520, 95), (0, 0, 0), -1)
        cv2.putText(frame, f"Logged Objects Count: {len(unique_tracked_ids)}", 
                    (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "Mode: Multi-Variation Fine-Grained Zero-Shot", 
                    (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        cv2.imshow("Universal AI Multi-Object & Restricted Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    alert_executor.shutdown(wait=False)

if __name__ == "__main__":
    process_video_or_webcam(source=0)