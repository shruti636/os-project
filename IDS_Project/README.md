# 🛡️ Machine Learning-Based Intrusion Detection System
**A Core Operating Systems Concept Project: Real-Time System Call Intrusion Monitoring utilizing Artificial Intelligence.**

This project bypasses traditional static signature-based detection models and implements **Behavioral Machine Learning (Random Forest Analysis)**. It physically hooks onto operating system processes, streaming live I/O metrics and kernel actions natively, to heuristically calculate malicious probabilities.

## 🌟 Key Architectural Features

### 1. 🌐 Cross-Platform OS Hooking
This project physically tracks actual processes without relying on static log files or simulations.
- **Linux Environment:** Hooks directly via Kernel traces utilizing `strace` for exact context-switch sequences.
- **Windows Environment:** Deploys a custom Kernel I/O Metric Translation pipeline utilizing `psutil`. It dynamically samples Delta File Handles, CPU R/W Operations, and Network Bindings, synthesizing standard POSIX System Calls (`read`, `write`, `socket`) dynamically on the fly to bridge the architectural divide.

### 2. 🧠 Self-Healing Neural Engine (Auto-Training)
The system is built with a highly resilient backend wrapper.
- If pre-calculated `RandomForestClassifier` `.pkl` model files are missing or corrupted, the system detects it upon launch.
- It pauses execution, locates your browser (Normal logic), triggers safe mock ransomware (Malicious logic), traces their behavior natively on your OS, and trains a fresh AI Neural Network completely autonomously in 15 seconds.

### 3. 🔥 Real-Time Pipeline Integration
- Analyzes System Calls dynamically in chunks (*n-grams*) instead of individually, keeping memory limits low while finding sequence-based patterns.
- Flask backend dynamically routes JSON predictions natively to the frontend over `CORS`.

---

## 🚀 Getting Started (One-Click Launch)

### **A. Windows (Natively)**
We have engineered a flawless 1-click startup bypass for Windows devices.
1. Download Python from the [Microsoft Store] or [Python.org].
2. Open the project folder (`IDS_Project`).
3. Double-click the **`start_ids_dashboard.bat`** file.
4. Watch as it safely installs requirements, bootstraps the ML engine, and launches your web browser connected to real system data seamlessly.

### **B. Linux / WSL (Advanced OS Hooking)**
Use standard CLI implementation utilizing root kernel permissions.
```bash
sudo apt install strace 
python -m pip install -r requirements.txt
sudo python app.py
```

---

## 🎓 OS Viva Potential Questions & Answers

**Q: Why use System Call monitoring over network packet monitoring?**
**A:** System calls (`open`, `read`, `socket`) are the fundamental language between the Operating System (Kernel Space) and applications (User Space). Even if an attacker encrypts their network traffic, their payload still *must* request physical OS resources (like creating a file or mutating permissions). We catch the physical OS interaction itself.

**Q: Why use Random Forest Machine Learning?**
**A:** Antiviruses look for *Signatures* (known virus hashes). This approach fails against "Zero-Day" attacks. Our Random Forest approach detects anomalies based purely on generic *Behavior* (e.g., executing `open` 500 times in 1 second alongside network `binds` indicates ransomware), allowing it to identify previously completely unknown viruses.

**Q: How does this work natively on Windows if `strace` is Linux exclusive?**
**A:** We wrote a custom hardware polling wrapper using `psutil`. Instead of grabbing physical syscall logs, the wrapper targets active CPU threads and measures exact delta changes in Read/Write bytes and Socket connections exactly every 0.3 seconds. We map these physical delta spikes to mock posix system calls (i.e. generating continuous `read`, `write`, `socket` feeds), feeding the ML Engine perfect metrics without breaking the Windows architecture.
