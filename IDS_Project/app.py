import os
import psutil
import threading
from flask import Flask, render_template, jsonify
from detector import RealTimeDetector
from real_time_collector import events_queue, monitor_live_process
from utils import logger, ensure_dirs

app = Flask(__name__)

detector = None
monitoring_active = False
monitored_pids = []

try:
    detector = RealTimeDetector()
    monitoring_active = True
except Exception as e:
    logger.error(f"Failed to load ML models. Ensure you trained on REAL data first: {e}")

def start_real_tracing():
    """Finds a few active processes on Linux and hooks strace to them."""
    if not monitoring_active: return
    
    # Let's target the current python process itself as a baseline safe monitor
    my_pid = os.getpid()
    monitored_pids.append(my_pid)
    t = threading.Thread(target=monitor_live_process, args=(my_pid, detector, 20, "Flask_Backend"), daemon=True)
    t.start()
    
    # Try finding an active dummy/malware simulator if it's running
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and 'malware_simulator.py' in ' '.join(proc.info['cmdline']):
                monitored_pids.append(proc.info['pid'])
                t2 = threading.Thread(target=monitor_live_process, args=(proc.info['pid'], detector, 20, "Malware_Simulator"), daemon=True)
                t2.start()
        except:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    total = len(events_queue)
    malicious = sum(1 for e in events_queue if e['status'] == 'MALICIOUS')
    safe = total - malicious
    
    # Determine the status
    has_strace = False
    try:
        # Check if strace is successfully functioning on OS
        import subprocess
        subprocess.run(["strace", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        has_strace = True
    except FileNotFoundError:
        has_strace = False

    status_str = "ACTIVE DEFENSE (REAL-TIME)" if (monitoring_active and has_strace) else ("OFFLINE - RUN IN LINUX/WSL" if not has_strace else "OFFLINE - RETRAIN MODEL")

    return jsonify({
        "total": total,
        "safe": safe,
        "malicious": malicious,
        "status": status_str,
        "monitored_pids": monitored_pids
    })

@app.route('/api/events')
def get_events():
    return jsonify(events_queue[:50])

if __name__ == '__main__':
    start_real_tracing()
    # Runs the web dashboard
    app.run(host='0.0.0.0', port=5000, debug=False)
