# 🛡️ AI Real-Time Security & Multi-Object Monitoring System

An advanced, lightweight zero-shot real-time object detection and security surveillance web application powered by **YOLO-World**, **OpenCV**, **SQLite**, and **Streamlit**.

---

## 🌟 Key Features

- **Zero-Shot Object Detection:** Detects open-vocabulary objects (e.g., knives, lead pencils, ID cards, wallets, watches, phones) in real-time without fine-tuning model weights.
- **Interactive Streamlit Dashboard:** Live video feed rendering with customizable detection confidence thresholds and object target settings.
- **Automated Security Alerts:** Asynchronous notification module triggering instant Gmail alerts upon detecting restricted or threat items.
- **Audit Logging & Database:** Integrated SQLite database to maintain continuous event logs, timestamps, and detection histories.
- **Lightweight Architecture:** Optimized for quick deployment, bypassing heavy binary files and local virtual environments.

---

## 🛠️ Tech Stack

- **Primary Language:** Python 3.10+
- **Computer Vision:** OpenCV, YOLO-World (Ultralytics)
- **Deep Learning Framework:** PyTorch / Torchvision
- **Web Interface:** Streamlit
- **Database:** SQLite3

---

## 📁 Repository Structure

```text
Restricted_Object_Detection/
├── src/
│   ├── counting.py       # Core YOLO-World detection & object counting engine
│   ├── database.py       # SQLite logger for security events
│   └── alerts.py         # Email alert notification trigger logic
├── app.py                # Main Streamlit web application interface
├── requirements.txt      # Project dependencies list
├── .gitignore            # Excluded runtime binaries, weights, and venv
└── README.md             # Project documentation
