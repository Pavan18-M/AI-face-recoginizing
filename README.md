# AI Face Recognition Attendance System

A production-ready, full-stack **AI Face Recognition Attendance System** built using Flask (backend), PyTorch (custom FaceCNN), OpenCV (face detection/alignment), SQLite, and Bootstrap 5 (responsive dark/light frontend). 

The system captures student face datasets directly from the webcam, trains a custom neural network, detects student faces in real-time, logs attendance, sends email alerts, and produces detailed reports (Excel, CSV, PDF).

---

## 🚀 Key Features

*   **Real-time Recognition:** Uses HTML5 Canvas webcam streams, OpenCV Haar Cascades for detection, and a PyTorch CNN for classification (80% confidence threshold).
*   **Voice Assistance:** Integrated Web Speech API (`speechSynthesis`) that reads out recognized student names and warnings.
*   **Role-Based Portals:**
    *   **Admin:** Complete student/faculty CRUD, database backup/restore, system event log inspector, model training control panel.
    *   **Faculty:** View assigned subjects, enroll student lists, and launch camera attendance marking.
    *   **Student:** View personal logs, subject-wise attendance percentages (warning under 75%), generate a digital Student ID Card with an embedded QR Code.
*   **Analytics Dashboards:** Live stats widgets and interactive Chart.js visualizations.
*   **Reporting:** Exporters to compile attendance records to styled Excel, standard CSV, or printable PDF formats (using ReportLab).
*   **Backups:** Auto-timestamped SQLite backups and restore points.

---

## 🛠️ Tech Stack

*   **Backend:** Flask, Flask-Login, Flask-SQLAlchemy (SQLite)
*   **AI/Vision:** OpenCV (Haar Cascades), PyTorch (CPU-only), Torchvision, Scikit-Learn
*   **Frontend:** HTML5, CSS3 (variables light/dark toggling), JavaScript (Webcam capture API), Bootstrap 5, Chart.js, SweetAlert2, QRCode.js

---

## 📦 Getting Started

### Method 1: The One-Click Launcher (Windows)
Double-click the launcher script at the root directory:
```bash
run_app.bat
```
This batch script will automatically create a virtual environment, activate it, install all dependencies (including lightweight PyTorch CPU), and run the Flask application.

### Method 2: Manual Setup
1.  **Create and activate virtual environment:**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    python app.py
    ```
4.  **Open browser:** Navigate to `http://localhost:5000`

---

## 🔐 Seeded Accounts for Testing

The database initializes and seeds the following mockup users for convenience:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `adminpassword` | Full system control panel |
| **Faculty** | `faculty` | `facultypassword` | Assigned subjects: AI, Computer Networks |
| **Student** | `student` | `studentpassword` | Enrolled: Computer Science, ID: CS-2026-001 |

---

## 📂 Project Structure

```
AI_Face_Recognition_Attendance_System/
│
├── backend/
│   ├── ai/
│   │   ├── detector.py        # Haar Cascade detector & face alignment
│   │   ├── model.py           # Custom FaceCNN PyTorch model
│   │   ├── dataset.py         # Face Dataset Loader & Augmentations
│   │   ├── trainer.py         # PyTorch Model training loop & curves
│   │   └── haarcascade_frontalface_default.xml
│   │
│   ├── db_models.py           # SQLAlchemy schemas (User, Student, Attendance)
│   ├── db_manager.py          # Database initializer and mock data seeder
│   ├── auth.py                # Authentication blueprint routes
│   ├── routes_api.py          # REST APIs (inference, capture, backup, exports)
│   ├── email_service.py       # Notification templates
│   ├── backup_manager.py      # SQLite copier & restoration
│   └── reports_generator.py   # PDF, Excel & CSV compilers
│
├── static/
│   ├── css/
│   │   └── style.css          # Design system & dark mode selectors
│   ├── js/
│   │   ├── app.js             # General sidebar & SweetAlert wrappers
│   │   ├── webcam.js          # Browser webcam interface, capture & speech loops
│   │   └── dashboard.js       # Chart.js analytics loaders
│   └── images/
│       └── plots/             # Model training curve exports
│
├── templates/                 # Bootstrap HTML views
│   ├── base.html              # Collapsible sidebar layouts
│   ├── login.html             # Glassmorphic login forms
│   ├── register.html          # Student vs Faculty selectors
│   ├── dashboard_*.html       # Role specific analytics dashboards
│   └── *_mgmt.html            # Data forms and camera panels
│
├── database/                  # Holds persistence attendance.db
├── dataset/                   # Dataset crops (student_<id>/face_001.jpg)
├── models/                    # Model weights mapping files
├── run_app.bat                # Windows quick launcher
├── Dockerfile                 # Docker image configuration
├── requirements.txt           # Project dependencies
└── app.py                     # Main application entry point
```
