/**
 * SOC Canary Dashboard Logic v1.6
 * AUTHOR: Vincent Priestley
 * DESCRIPTION: Handles live telemetry, fleet management, and remote commands.
 * British English: First-person commentary, uniform across environment.
 */

let lastDataHash = "";

/** I'm polling the vault for new threat logs and forensic snapshots. */
async function updateDashboard() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        const currentHash = JSON.stringify(data.logs);
        if (currentHash === lastDataHash) return; 
        lastDataHash = currentHash;

        // I'm rendering the incident feed with the restored 'action' mapping
        const logContainer = document.getElementById('inner-logs');
        if (logContainer) {
            logContainer.innerHTML = data.logs.length > 0 ? data.logs.map(log => `
                <div class="incident-entry" style="border-left: 4px solid #ff4d4d; padding: 15px; margin-bottom: 10px; background: rgba(255, 77, 77, 0.05);">
                    <strong style="color: #ff4d4d;">[${log.time}] ${log.action || 'THREAT DETECTED'}</strong><br>
                    <span>AGENT: ${log.hostname} | FILE: ${log.file}</span>
                </div>
            `).join('') : '<p style="color: #475569; text-align: center; margin-top: 50px;">NO ACTIVE BREACHES DETECTED</p>';
        }

        // I'm restoring the Forensic Snapshot Gallery
        const gallery = document.getElementById('snapshot-gallery');
        if (gallery) {
            const snapshots = data.logs.filter(l => l.image && l.image !== "None");
            gallery.innerHTML = snapshots.length > 0 ? snapshots.map(log => `
                <div class="gallery-item" style="margin-bottom: 15px; border: 1px solid #1e293b; background: #020617; padding: 5px;">
                    <a href="/static/screenshots/${log.image}" target="_blank">
                        <img src="/static/screenshots/${log.image}" style="width: 100%; display: block;" onerror="this.src='/static/img/placeholder.png'">
                    </a>
                    <div style="font-size: 0.65rem; color: #64748b; margin-top: 5px; text-align: center;">
                        ${log.time} - ${log.hostname}
                    </div>
                </div>
            `).join('') : '<p style="color: #475569; font-size: 0.8rem; text-align: center;">Waiting for forensic evidence...</p>';
        }
    } catch (err) { console.error("I failed to refresh the telemetry feed."); }
}

/** I'm updating the status and command capabilities of every agent in the fleet. */
async function refreshFleetStatus() {
    try {
        const response = await fetch('/api/fleet');
        const fleet = await response.json();
        const container = document.getElementById('fleet-list');
        if (!container) return;

        container.innerHTML = Object.entries(fleet).map(([name, info]) => `
            <div class="fleet-card" style="padding: 15px; border: 1px solid #1e293b; margin-bottom: 10px; background: #0f172a;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: ${info.status === 'ONLINE' ? '#10b981' : '#ef4444'}">${name}</strong>
                    <span style="font-size: 0.7rem; color: #64748b;">${info.ip}</span>
                </div>
                <p style="font-size: 0.75rem; margin: 10px 0; color: #94a3b8;">Current Path: ${info.current_path}</p>
                <div style="display: flex; gap: 5px;">
                    <button onclick="manageAgent('${name}')" class="nav-btn" style="flex: 1; font-size: 0.7rem; padding: 5px;">POLICY</button>
                    <button onclick="triggerWipe('${name}')" class="nav-btn" style="flex: 1; font-size: 0.7rem; padding: 5px; border-color: #ef4444; color: #ef4444;">WIPE</button>
                </div>
            </div>
        `).join('');
    } catch (err) { console.error("I lost connection to the fleet manager."); }
}

/** I'm loading the specific security rules for an agent. */
async function manageAgent(hostname) {
    const title = document.getElementById('policy-target-title');
    const pathInput = document.getElementById('admin-path-input');
    const extInput = document.getElementById('admin-ext-input');
    const lockToggle = document.getElementById('auto-lock-toggle');

    if (title) title.innerText = hostname ? `MANAGING AGENT: ${hostname}` : "GLOBAL SYSTEM POLICY";
    if (pathInput) pathInput.dataset.targetHost = hostname || "GLOBAL";

    try {
        const url = hostname ? `/api/config/${hostname}` : '/api/config';
        const res = await fetch(url);
        const config = await res.json();

        // I'm populating the inputs carefully to avoid null errors
        if (pathInput) pathInput.value = Array.isArray(config.watch_paths) ? config.watch_paths.join(', ') : config.watch_paths;
        if (extInput) extInput.value = Array.isArray(config.extensions) ? config.extensions.join(', ') : config.extensions;
        if (lockToggle) lockToggle.checked = config.auto_lock || false;

        showTab('policy');
    } catch (err) { console.error("I couldn't retrieve the requested policy."); }
}

/** I'm pushing the new policy to the backend and the remote agent. */
async function applySecurityPolicy() {
    const pathInput = document.getElementById('admin-path-input');
    const extInput = document.getElementById('admin-ext-input');
    const lockToggle = document.getElementById('auto-lock-toggle');
    const targetHost = pathInput ? pathInput.dataset.targetHost : "GLOBAL";

    const payload = {
        hostname: targetHost,
        is_global: targetHost === "GLOBAL",
        watch_path: pathInput ? pathInput.value : "",
        extensions: extInput ? extInput.value.split(',').map(e => e.trim()) : [],
        auto_lock: lockToggle ? lockToggle.checked : false
    };

    try {
        await fetch('/api/policies/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        alert(`Security policy synchronised for ${targetHost}.`);
    } catch (err) { alert("I failed to synchronise the policy."); }
}

async function triggerWipe(hostname) {
    if (confirm(`Are you certain you want to WIPE monitored sectors on ${hostname}? This cannot be undone.`)) {
        await fetch(`/api/fleet/wipe/${hostname}`, { method: 'POST' });
        alert("Wipe command dispatched.");
    }
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('active-flex');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    const target = document.getElementById(`${tabName}-view`);
    if (tabName === 'telemetry') {
        target.classList.add('active-flex');
        target.classList.remove('hidden');
        updateDashboard(); // I'm forcing the screenshot refresh here
    } else {
        target.classList.remove('hidden');
    }
    document.getElementById(`btn-${tabName}`).classList.add('active');
}

/** I'm sending the deletion request to the vault. */
async function deleteLog(time, file) {
    if (!confirm("I am about to purge this forensic entry. Proceed?")) return;

    try {
        await fetch('/api/logs/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time: time, file: file })
        });
        // I'm clearing the hash so the UI forces a re-render immediately
        lastDataHash = "";
        updateDashboard();
    } catch (err) { console.error("I failed to delete the entry."); }
}

async function purgeAllLogs() {
    if (!confirm("CRITICAL: Wipe all forensic history?")) return;
    try {
        await fetch('/api/logs/purge', { method: 'DELETE' });
        lastDataHash = ""; 
        updateDashboard(); // I'm clearing the UI immediately
    } catch (err) { console.error("I couldn't purge the logs."); }
}

// I'm starting the security heartbeat loops
setInterval(updateDashboard, 2000);
setInterval(refreshFleetStatus, 3000);

// Initial bootstrap
updateDashboard();
refreshFleetStatus();