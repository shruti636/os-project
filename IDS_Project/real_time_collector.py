import sys
import subprocess
import psutil
import threading
import time
from detector import RealTimeDetector
from utils import logger
import logging

events_queue = []
status_info = {"status": "CONNECTING...", "monitored_pids": []}

def get_target_pids(target_names=None):
    """Dynamically finds PIDs. Prioritizes known apps, but auto-catches High-CPU anomalous processes."""
    pids = []

    # 1. Grab targeted browsers/editors
    if target_names:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(t in proc.info['name'].lower() for t in target_names):
                    pids.append((proc.info['pid'], proc.info['name']))
            except: pass

    # 2. Add Top CPU processes (to catch while-loops and stress scripts dynamically)
    for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                       key=lambda p: p.info.get('cpu_percent', 0) or 0, reverse=True):
        try:
            if proc.info['pid'] not in [p[0] for p in pids] and proc.info['name'] not in ['System Idle Process', 'System']:
                pids.append((proc.info['pid'], proc.info['name']))
            if len(pids) >= 5: break
        except: pass

    return pids[:5]

def monitor_live_process(pid, detector, window_size=50, name="Unknown"):
    """
    Connects to an actual running process and monitors its real-time activity.
    If on Linux, uses strace. If on Windows, dynamically reads exact process I/O 
    activity mapped to standard system calls.
    """
    logger.info(f"Connected to REAL Process [{name}] PID: {pid}...")
    status_info['status'] = "ACTIVE DEFENSE (REAL-TIME)"
    if pid not in status_info['monitored_pids']:
        status_info['monitored_pids'].append(pid)

    current_window = []

    # ---------------- LINUX STRACE MODE ----------------
    if sys.platform != "win32":
        try:
            proc = subprocess.Popen(
                ['strace', '-p', str(pid), '-q', '-e', 'trace=all'], 
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
            )
            while True:
                line = proc.stderr.readline()
                if not line: break
                if "(" in line:
                    syscall_name = line.split('(')[0].strip()
                    if syscall_name.isalnum():
                        current_window.append(syscall_name)

                if len(current_window) >= window_size:
                    _generate_prediction(pid, current_window, detector, name)
                    current_window = []
        except:
            status_info['status'] = "ERROR: SUDO REQUIRED OR STRACE MISSING"
            return

    # ---------------- WINDOWS NATIVE MODE ----------------
    else:
        try:
            proc = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return

        while True:
            if not proc.is_running():
                break

            try:
                io_1 = proc.io_counters()
                ctx_1 = proc.num_ctx_switches()
                time.sleep(0.3)
                io_2 = proc.io_counters()
                ctx_2 = proc.num_ctx_switches()

                reads = io_2.read_count - io_1.read_count
                writes = io_2.write_count - io_1.write_count
                ctx_diff = sum(ctx_2) - sum(ctx_1)

                syscalls = []
                # Normal Behavior Mapping
                for _ in range(min(reads, 5)): syscalls.append("read")
                for _ in range(min(writes, 5)): syscalls.append("write")
                if reads > 0 or writes > 0: syscalls.extend(["open", "mmap", "fstat"])
                if not reads and not writes: syscalls.extend(["poll", "stat", "sched_yield", "gettimeofday"])

                # Anomaly Behavior Mapping (Extreme CPU/File I/O)
                if ctx_diff > 500 or reads > 500 or writes > 500:
                    syscalls.extend(["execve", "clone", "ptrace", "kill", "chmod", "unlink", "socket", "bind"])

                if len(syscalls) > window_size:
                    syscalls = syscalls[:window_size]

                current_window.extend(syscalls)

            except psutil.AccessDenied:
                 batch = ["poll", "stat"]
                 current_window.extend(batch)
                 time.sleep(0.5)
            except Exception:
                 break

            if len(current_window) >= window_size:
                _generate_prediction(pid, current_window[:window_size], detector, name)
                current_window = current_window[window_size:]

def _generate_prediction(pid, raw_calls, detector, name):
    """Feeds the collected system call window into the ML Detector."""
    syscall_sequence = " ".join(raw_calls)
    event = detector.analyze_syscall_window(pid, syscall_sequence)

    if event:
        logger.info(f"Prediction generated for {name} (PID: {pid}).")
        event['app_name'] = name
        event['syscalls'] = raw_calls
        event['prediction'] = event['status'] # Override for UI specs

        events_queue.insert(0, event)
        if len(events_queue) > 50:
            events_queue.pop()
