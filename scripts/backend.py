# =================================================================
# PROJECT: HYBRID CANARY SYSTEM V1.6
# AUTHOR: Vincent Priestley
# DESCRIPTION: Full-Feature Backend. Handles Forensics & Fleet Cmds.
# British English: First-person commentary, real-world architecture.
# =================================================================

import os, datetime, json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- SYSTEM SETUP ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
LOG_FILE = os.path.join(BASE_DIR, "security_log.txt")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# I'm ensuring the forensic vault is ready to receive snapshots
SCREENSHOT_DIR = os.path.join(STATIC_DIR, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FLEET_STATUS = {}
COMMAND_QUEUE = {}
AGENT_POLICIES = {}

# I've added auto_lock as a toggleable policy feature
GLOBAL_POLICY = {
    "watch_paths": ["C:\\CanaryTest"],
    "watch_files": [], 
    "extensions": [".txt", ".pdf", ".docx"],
    "auto_lock": False
}

def write_log(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# --- API CORE ---

@app.get("/")
async def serve_dashboard():
    with open(os.path.join(TEMPLATES_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/alert")
async def receive_alert(request: Request):
    """ I'm recording the breach and checking if I need to trigger an auto-lock. """
    data = await request.json()
    host = data.get("hostname", "UNKNOWN")
    
    entry = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "hostname": host,
        "file": data.get("file_path", "N/A"),
        "action": "CRITICAL BREACH",
        "image": data.get("image", "None")
    }
    write_log(entry)

    # I'm checking the policy to see if this agent should lock down immediately
    policy = AGENT_POLICIES.get(host, GLOBAL_POLICY)
    if policy.get("auto_lock"):
        COMMAND_QUEUE[host] = "LOCK_WORKSTATION"
    
    return {"status": "recorded"}

@app.get("/api/logs")
async def get_logs():
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try: logs.append(json.loads(line))
                    except: continue
    return {"logs": logs[::-1]}

@app.get("/api/config")
async def get_global(): return GLOBAL_POLICY

@app.get("/api/config/{hostname}")
async def get_config(hostname: str):
    return AGENT_POLICIES.get(hostname, GLOBAL_POLICY)

@app.post("/api/policies/update")
async def update_policy(request: Request):
    data = await request.json()
    config = {
        "watch_paths": [p.strip() for p in data.get("watch_path", "").split(',') if p.strip()],
        "watch_files": [f.strip() for f in data.get("watch_files", "").split(',') if f.strip()],
        "extensions": data.get("extensions", []),
        "auto_lock": data.get("auto_lock", False)
    }
    if data.get("is_global"):
        global GLOBAL_POLICY
        GLOBAL_POLICY = config
    else:
        AGENT_POLICIES[data.get("hostname")] = config
    return {"status": "success"}

@app.post("/api/heartbeat")
async def heartbeat(request: Request):
    data = await request.json()
    host = data.get("hostname")
    FLEET_STATUS[host] = {
        "ip": data.get("ip"),
        "last_seen_raw": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_path": data.get("current_path", "IDLE")
    }
    return {"status": "ok", "command": COMMAND_QUEUE.pop(host, None)}

@app.get("/api/fleet")
async def get_fleet():
    now = datetime.datetime.now()
    processed = {}
    for host, info in FLEET_STATUS.items():
        ls = datetime.datetime.strptime(info['last_seen_raw'], "%Y-%m-%d %H:%M:%S")
        delta = (now - ls).total_seconds()
        processed[host] = {
            "ip": info["ip"],
            "status": "ONLINE" if delta < 30 else "DISCONNECTED",
            "last_seen": f"{int(delta)}s ago",
            "current_path": info["current_path"]
        }
    return processed

@app.post("/api/fleet/wipe/{hostname}")
async def queue_wipe(hostname: str):
    COMMAND_QUEUE[hostname] = "WIPE_CANARIES"
    return {"status": "wipe_queued"}

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.delete("/api/logs/delete")
async def delete_log(request: Request):
    """ I'm removing a specific entry from the forensic log file. """
    params = await request.json()
    target_time = params.get("time")
    target_file = params.get("file")
    
    updated_logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                log = json.loads(line)
                # I'm keeping everything except the specific match
                if not (log.get("time") == target_time and log.get("file") == target_file):
                    updated_logs.append(line)
        
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(updated_logs)
            
    return {"status": "success"}

@app.delete("/api/logs/purge")
async def purge_logs():
    """ I'm clearing out the entire forensic log file. """
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("") # I'm just emptying the file
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)