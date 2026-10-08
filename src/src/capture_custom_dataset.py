import os
import cv2

def capture_dataset(item_name="atm_card", num_samples=20):
    save_dir = os.path.abspath(f"dataset/custom_images/{item_name}")
    os.makedirs(save_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print(f"\n[INFO] Show your {item_name.upper()} in front of camera!")
    print("Press 'SPACE' to capture photo, 'q' to stop early.\n")

    count = 0
    while cap.isOpened() and count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        # Show counter overlay
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Capturing '{item_name}': {count}/{num_samples} (Press SPACE)", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Custom Dataset Collector", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            save_path = os.path.join(save_dir, f"{item_name}_{count}.jpg")
            cv2.imwrite(save_path, frame)
            print(f"Saved: {save_path}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[SUCCESS] Saved {count} custom images to {save_dir}")

if __name__ == "__main__":
    capture_dataset(item_name="atm_card", num_samples=20)