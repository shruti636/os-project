import subprocess
import psutil
import threading
from detector import RealTimeDetector
from utils import logger
import logging
# Add to global events list in memory if requested
events_queue = []

def get_top_pids(limit=5):
    """Fetch top running user processes to monitor."""
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if proc.info['cpu_percent'] > 0.0 and proc.info['pid'] > 100:
                pids.append((proc.info['pid'], proc.info['name']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    # Return top 'limit' active processes
    return sorted(pids, key=lambda x: x[1], reverse=True)[:limit]

def monitor_live_process(pid, detector, window_size=20, name="Unknown"):
    """
    Monitor a live Linux process using strace. 
    Gathers system calls dynamically and feeds them straight into the IDS model.
    """
    logger.info(f"Attaching strace to LIVE process [{name}] PID: {pid}...")
    
    try:
        # We capture raw output from strace 
        # -p attaches to process, -q suppresses attach messages
        cmd = ['strace', '-p', str(pid), '-q']
        proc = subprocess.Popen(
            cmd, 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        logger.error("[CRITICAL] 'strace' is not installed or using Windows Native.")
        logger.error("Run this inside Ubuntu/WSL: sudo apt-get install strace")
        return

    current_window = []
    
    while True:
        line = proc.stderr.readline()
        if not line and proc.poll() is not None:
            # Proc died
            logger.info(f"Process {pid} terminated naturally.")
            break
            
        try:
            syscall_name = line.split('(')[0].strip()
            
            if syscall_name.isalnum():
                current_window.append(syscall_name)
                
            if len(current_window) >= window_size:
                syscall_sequence = " ".join(current_window)
                
                # Inference Time!
                event = detector.analyze_syscall_window(pid, syscall_sequence)
                
                if event:
                    event['app_name'] = name
                    events_queue.insert(0, event)
                    if len(events_queue) > 100:
                        events_queue.pop()
                    
                    if event['status'] == "MALICIOUS":
                        # Turn off heavy logging for smooth dashboard, just log warnings
                        logger.warning(f"🚨 ACTIVE THREAT: PID {pid} [{name}] Confidence: {event['confidence']}%")
                        
                current_window = []
                
        except Exception:
            continue

def spawn_multi_process_monitors(pids, detector):
    """Spawns individual strace threads for multiple processes."""
    threads = []
    for pid, name in pids:
        t = threading.Thread(target=monitor_live_process, args=(pid, detector, 20, name), daemon=True)
        t.start()
        threads.append(t)
    return threads

if __name__ == "__main__":
    import sys
    detector = RealTimeDetector()
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
        monitor_live_process(pid, detector)
    else:
        print("Finding active process to trace...")
        top_pids = get_top_pids(1)
        if top_pids:
            monitor_live_process(top_pids[0][0], detector, name=top_pids[0][1])
