# =================================================================
# PROJECT: HYBRID CANARY SYSTEM V1.6
# AUTHOR: Vincent PriestLEY
# DESCRIPTION: Full-Feature Agent. Snapshot, Lock, & Wipe capable.
# British English: First-person commentary, .pyw for background.
# =================================================================

import time, requests, os, socket, shutil, pyautogui
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HOSTNAME = socket.gethostname()
IP_ADDR = socket.gethostbyname(HOSTNAME)
VAULT_URL = "http://127.0.0.1:8000/api"

class CanaryHandler(FileSystemEventHandler):
    def __init__(self, exts):
        self.exts = exts

    def on_modified(self, event):
        if not event.is_directory:
            ext = os.path.splitext(event.src_path)[1].lower()
            if ext in self.exts:
                # I'm capturing forensic evidence immediately
                ts = int(time.time())
                img_name = f"snap_{ts}_{HOSTNAME}.png"
                # I'm saving to the common static/screenshots folder
                img_path = os.path.join(os.getcwd(), "static", "screenshots", img_name)
                
                try:
                    pyautogui.screenshot(img_path)
                except: img_name = "None"

                try:
                    requests.post(f"{VAULT_URL}/alert", json={
                        "file_path": event.src_path, 
                        "hostname": HOSTNAME,
                        "image": img_name
                    })
                except: pass

class RemoteSensor:
    def __init__(self):
        self.paths, self.exts = [], []
        self.observers = []

    def wipe_sectors(self):
        """ I'm purging the monitored directories as requested by the SOC. """
        for p in self.paths:
            if os.path.exists(p) and "Windows" not in p: # Basic safety check
                try: shutil.rmtree(p)
                except: pass

    def run(self):
        while True:
            try:
                # Pulse & Command Check
                res = requests.post(f"{VAULT_URL}/heartbeat", json={
                    "hostname": HOSTNAME, "ip": IP_ADDR, "current_path": str(self.paths)
                }, timeout=3)
                
                cmd = res.json().get("command")
                if cmd == "LOCK_WORKSTATION":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                elif cmd == "WIPE_CANARIES":
                    self.wipe_sectors()

                # Policy Update
                pol = requests.get(f"{VAULT_URL}/config/{HOSTNAME}", timeout=3).json()
                if pol.get("watch_paths") != self.paths or pol.get("extensions") != self.exts:
                    self.paths, self.exts = pol["watch_paths"], pol["extensions"]
                    for o in self.observers: o.stop()
                    self.observers = []
                    for p in self.paths:
                        if os.path.exists(p):
                            obs = Observer()
                            obs.schedule(CanaryHandler(self.exts), p, recursive=False)
                            obs.start()
                            self.observers.append(obs)
            except Exception as e: print(f"[-] Comms error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    RemoteSensor().run()