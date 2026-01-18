# 🛡️ HYBRID CANARY SYSTEM v1.6
**Author:** Vincent Priestley

### Architecture Overview
This system uses a **FastAPI Backend** to manage a fleet of **Remote Sensors**. 
- **Forensics:** Captures snapshots using `pyautogui` on breach.
- **Fleet Command:** Remote "Wipe" and "Lock" capabilities.
- **Policy:** Dynamic synchronization of watched paths and extensions.



### Quick Start
1. Run `pip install fastapi uvicorn watchdog requests pyautogui`
2. Start the Vault: `python backend.py`
3. Deploy Agent: `python sensor.py` (ensure it points to the Vault IP)