import os
import threading
from flask import Flask, render_template, jsonify
# Flask CORS is standard to fix frontend fetch issues when double clicking HTML files.
try:
    from flask_cors import CORS
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-cors"])
    from flask_cors import CORS

from detector import RealTimeDetector
from real_time_collector import events_queue, status_info, get_target_pids, monitor_live_process
from utils import logger

app = Flask(__name__)
# Allow cross-origin if you open index.html without a web server
CORS(app)

detector = None

try:
    detector = RealTimeDetector()
except Exception as e:
    logger.warning("Neural Engine Models not found! AUTO-TRAINING Pipeline Initiated...")
    status_info['status'] = "GENERATING REAL OS DATASET..."
    try:
        from main import execute_pipeline
        execute_pipeline() # Automatically harvests windows data & trains the Random Forest
        detector = RealTimeDetector()
        status_info['status'] = "CONNECTING..."
    except Exception as inner_e:
        logger.error(f"Auto-Training completely failed. Missing Libraries? {inner_e}")
        status_info['status'] = f"ERROR: {str(inner_e).upper()}"

def start_real_tracing():
    """Automatically finds REAL browsers or editors to monitor upon Flask boot."""
    if not detector: return

    # We are explicitly searching for these real local programs, PLUS any High-CPU Anomalies:
    targets = get_target_pids(['chrome', 'code', 'brave', 'msedge'])

    if targets:
        logger.info(f"Found {len(targets)} valid targets. Connecting threads...")
        for pid, name in targets:
            # Pushing window_size to 50 for enhanced N-gram sequencing
            t = threading.Thread(target=monitor_live_process, args=(pid, detector, 50, name), daemon=True)
            t.start()
    else:
        # Fallback to monitoring the python application itself if no browsers are open
        logger.warning("No Chrome or VSCode found. Monitoring self (Python Backend PID).")
        my_pid = os.getpid()
        t = threading.Thread(target=monitor_live_process, args=(my_pid, detector, 50, "System_Backend"), daemon=True)
        t.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    total = len(events_queue)
    malicious = sum(1 for e in events_queue if e['prediction'] == 'MALICIOUS')
    safe = total - malicious

    return jsonify({
        "total": total,
        "safe": safe,
        "malicious": malicious,
        "status": status_info['status'],
        "monitored_pids": status_info['monitored_pids']
    })

@app.route('/api/events')
def get_events():
    """Returns the precise JSON payload format expected by the frontend requirements."""
    output = []
    for evt in events_queue:
        output.append({
            "timestamp": evt['timestamp'],
            "pid": evt['pid'],
            "app_name": evt.get('app_name', 'Unknown'),
            "syscalls": evt.get('syscalls', []),
            "sequence_preview": evt.get('sequence_preview', ""),
            "prediction": evt['prediction'],  
            "confidence": evt['confidence']   
        })
    return jsonify(output)

if __name__ == '__main__':
    logger.info("Starting Backend Flask Pipeline...")
    start_real_tracing()
    logger.info("To interact, launch index.html or go to http://127.0.0.1:5000")
    # Bind to 127.0.0.1 explicitly to dodge firewall blocks restricting windows network ports
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
