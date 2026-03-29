import os
import subprocess
import time
import pandas as pd
from utils import logger, ensure_dirs

def run_strace(pid, duration=10):
    """Run strace on a given PID for a specific duration to collect raw syscalls."""
    logger.info(f"Collecting real system calls from PID {pid} for {duration} seconds...")
    try:
        # -p attaches to process, -c generates summary, but we need streaming:
        # We capture raw output. -e trace=all
        proc = subprocess.Popen(
            ['strace', '-p', str(pid), '-q'], 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        logger.error("[ERROR] strace not found. Ensure you are running on Linux/WSL. Install with 'sudo apt install strace'.")
        return []

    syscalls = []
    start_time = time.time()
    
    # Read output for 'duration' seconds
    while time.time() - start_time < duration:
        try:
            line = proc.stderr.readline()
            if not line:
                break
            # Parse syscall name: Example: "read(3, ...)"
            syscall_name = line.split('(')[0].strip()
            if syscall_name.isalnum():
                syscalls.append(syscall_name)
        except Exception:
            continue
            
    # Kill the strace process
    proc.terminate()
    return syscalls

def create_windows_from_syscalls(syscalls, window_size=30):
    """Chunks a list of syscalls into sentences of length 'window_size'."""
    windows = []
    for i in range(0, len(syscalls) - window_size + 1, window_size):
        windows.append(" ".join(syscalls[i:i + window_size]))
    return windows

def collect_training_data(normal_pid, malicious_pid, duration=30, output_file="data/real_dataset.csv"):
    """
    Collect real syscall data from two processes: one normal, one malicious.
    If you don't have a malicious one ready, run `python malware_simulator.py` first.
    """
    ensure_dirs()
    data = []

    # Collect Normal
    if normal_pid:
        normal_calls = run_strace(normal_pid, duration)
        normal_windows = create_windows_from_syscalls(normal_calls)
        for w in normal_windows:
            data.append({"sequence": w, "label": 0})
        logger.info(f"Collected {len(normal_windows)} normal sample windows.")

    # Collect Malicious
    if malicious_pid:
        mal_calls = run_strace(malicious_pid, duration)
        mal_windows = create_windows_from_syscalls(mal_calls)
        for w in mal_windows:
            data.append({"sequence": w, "label": 1})
        logger.info(f"Collected {len(mal_windows)} malicious sample windows.")

    if data:
        df = pd.DataFrame(data)
        # Shuffle
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv(output_file, index=False)
        logger.info(f"Real Dataset generated and saved to {output_file} with {len(df)} total samples.")
    else:
        logger.error("No data collected. Check if PIDs are valid and strace permissions (sudo) are granted.")
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: sudo python data_collection.py <NORMAL_PID> <MALICIOUS_PID> [duration_seconds]")
        sys.exit(1)
        
    n_pid = sys.argv[1]
    m_pid = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    collect_training_data(n_pid, m_pid, duration)
