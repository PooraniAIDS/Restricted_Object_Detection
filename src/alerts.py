import os
import cv2
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Direct Gmail Configuration
SENDER_EMAIL = "spooranisivaprakasam@gmail.com"
SENDER_APP_PASSWORD = "kcbf buzj njhl dnyd"  # Your 16-character App Password
RECEIVER_EMAIL = "spooranisivaprakasam@gmail.com"

def send_email_alert(category, confidence, frame):
    """
    Saves a snapshot image and sends an instant email alert via Gmail SMTP.
    """
    os.makedirs("results/alerts", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.abspath(f"results/alerts/alert_{category}_{timestamp}.jpg")
    
    # Save snapshot image locally
    cv2.imwrite(snapshot_path, frame)
    print(f"\n🚨 [SECURITY ALERT] Restricted Item: {category.upper()} ({confidence:.1f}%)")
    print(f"   Snapshot saved at: {snapshot_path}")

    try:
        msg = EmailMessage()
        msg['Subject'] = f"🚨 SECURITY ALERT: Restricted Item Detected ({category.upper()})"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        body_content = (
            f"⚠️ RESTRICTED THREAT DETECTED ⚠️\n\n"
            f"Item Name: {category.upper()}\n"
            f"Confidence Level: {confidence:.2f}%\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"An image snapshot of the threat is attached to this email."
        )
        msg.set_content(body_content)

        # Attach image snapshot
        with open(snapshot_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(snapshot_path)
            msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename=file_name)

        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            smtp.send_message(msg)
            
        print("   ✅ Gmail SMTP Alert dispatched successfully with snapshot attached!")

    except Exception as e:
        print(f"   [WARNING] Failed to send email alert: {e}")

if __name__ == "__main__":
    print("Alert engine loaded.")