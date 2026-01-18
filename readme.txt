================================================================
HYBRID CANARY: RANSOMWARE DETECTION & ACTIVE DEFENCE (v1.2)
================================================================

OVERVIEW
This project is a high-performance, real-time EDR (Endpoint 
Detection and Response) prototype. It utilizes a Python-based 
"Sensor" for robust Windows API monitoring and a FastAPI 
"Active Defence Brain" to neutralize threats and capture 
forensic evidence.

NEW IN V1.2:
- Forensic Capture: Automated desktop snapshots upon detection.
- System Lockdown: Immediate user logout via user32.dll call.
- Python Sensor: Switched to watchdog-based monitoring for 
  higher reliability and bypass of local sandbox interference.
- SOC Dashboard: Web UI for real-time incident tracking.

COMPONENTS:
1. sensor.py (Python): Uses Watchdog to hook into Windows 
   ReadDirectoryChangesW API for low-latency monitoring.
2. backend.py (Python): A FastAPI server that executes 
   mitigation (Process Kill), Forensics (Snapshot), and Lock.
3. snapshots/ : Directory containing visual proof of attacks.

PREREQUISITES:
- Python 3.12+ (managed via win_env virtual environment)
- Python Libraries: fastapi, uvicorn, psutil, pyautogui, watchdog
- Windows 10/11 (LockWorkStation support required)

PROJECT STRUCTURE:
/scripts/sensor.py  - Python Windows API watcher (The "Eyes").
/scripts/backend.py - Response & Forensics Engine (The "Brain").
/templates/         - SOC Dashboard UI files.
/snapshots/         - Automated forensic image storage.
/win_env/           - Python Virtual Environment.

EXECUTION:
1. Activate Environment & Start Backend:
   .\win_env\Scripts\activate
   python scripts/backend.py

2. Start the Sensor (In a second window):
   .\win_env\Scripts\activate
   python scripts/sensor.py

DETECTION & DEFENSE LOGIC:
1. MONITORING: The sensor watches 'C:\Users\Public\Documents\CanaryTest'.
2. DETECTION: Any file creation/rename triggers a JSON alert.
3. FORENSICS: Backend captures 'threat_TIMESTAMP.png' of desktop.
4. MITIGATION: Backend kills 'notepad.exe' and locks the workstation.

SECURITY NOTE:
This system is an "Active Defence" prototype. Ensure you are 
testing in the designated local directory.
================================================================