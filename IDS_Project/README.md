# Machine Learning-Based Intrusion Detection System
**using System Call Analysis**

This project is a real-time, behavior-based Intrusion Detection System (IDS). By analyzing the system call sequences of running processes, it uses a Machine Learning model (Random Forest) to label processes as either **SAFE** or **MALICIOUS**. 

Unlike signature-based antiviruses which search for known virus files, this system detects the *behavior* of zero-day attacks (like ransomware or rootkits) by looking at what the process is trying to do (e.g., repeatedly opening files, injecting processes, changing permissions).

---

## 📁 Project Structure

```text
IDS_Project/
│── data/                     # Where the synthetic syscall CSV is stored
│── models/                   # Pickled ML models (RF and TF-IDF feature extractor)
│── templates/                # HTML Dashboard UI
│   └── index.html
│── requirements.txt          # Python dependencies
│── utils.py                  # Logger and directory setup
│── data_collection.py        # Generates synthetic dataset simulating normal/malicious syscalls
│── feature_extraction.py     # N-Gram extraction using Scikit-Learn
│── model_training.py         # Trains the Random Forest classifier, saves model
│── detector.py               # The Core Inference engine evaluating streams of syscalls
│── app.py                    # Flask Web Application bringing everything together
│── main.py                   # Command-Line Testing Interface
```

---

## 🚀 Step-by-Step Execution Guide

### 1. Install Dependencies
Open your terminal (or Command Prompt / PowerShell) and navigate to the `IDS_Project` directory:
```bash
pip install -r requirements.txt
```

### 2. Generate the Dataset
We need system call logs to train the model. For this project, we generate a highly-realistic synthetic dataset.
```bash
python main.py --generate
```
*Expected Output: `dataset.csv` is created in the `data/` folder.*

### 3. Train the Machine Learning Model
Train the Random Forest Classifier on the generated dataset:
```bash
python main.py --train
```
*Expected Output: Prints Model Evaluation metrics (Accuracy, F1-Score) and saves `rf_model.pkl` and `extractor.pkl` to `models/`.*

### 4. Run the Real-Time Simulation (Terminal)
To test the real-time simulation engine via CLI:
```bash
python main.py --simulate
```
*Expected Output: Simulates live system call injections and alerts in the CLI (🚨 MALICIOUS or ✅ SAFE).*

### 5. Run the Beautiful Web Dashboard 🌟 (RECOMMENDED)
To fire up the graphical real-time dashboard:
```bash
python app.py
```
*Open `http://localhost:5000` in your web browser. You will see live dynamic monitoring of process IDs along with visual alerts when an attack sequence is detected!*

---

## 🎓 Guide for the OS Viva

Here is everything you need to confidently answer questions during your viva:

### 1. What is the core problem solved?
Traditional Antiviruses rely on "Signatures" (hashes of known viruses). If a virus changes its code by 1 bit, the signature fails. 
**Our Solution:** We use behavioral analysis. An attacker can change their code, but to steal data, they MUST use the OS's system calls (e.g., `open`, `read`, `socket`, `bind`). We analyze these syscall sequences.

### 2. How are System Calls captured?
In a full production Linux environment, we would use **eBPF (Extended Berkeley Packet Filter)** or `strace` to intercept context switches when user-space transitions to kernel-space. For this cross-platform mini-project, we implemented a highly representative **Simulation Engine** that generates streams of system calls akin to real background processes.

### 3. Feature Engineering: What are N-Grams?
A single system call (e.g., `open()`) is not inherently malicious. However, the sequence `open() -> read() -> socket() -> bind()` is highly suspicious (could be a reverse shell). 
We use **Scikit-Learn's CountVectorizer with N-grams**. It treats the sequence of system calls like words in a sentence, counting the frequency of continuous blocks of system calls. The ML model learns which sequences lead to "Malicious" vs "Normal" behavior.

### 4. Why Random Forest?
* **Interpretability:** We can actually see which system calls contribute most to an alert.
* **Non-Linear Data:** Feature frequency distributions of system calls are highly non-linear. Random Forests handle mixed numerical distributions much better than simple linear models (like Logistic Regression).
* **Speed:** Inference (predicting) on a trained tree is an O(log N) lookup path, making it extremely fast, which is critical for **real-time IDS systems** since thousands of system calls arrive per second.

### 5. System Architecture
1. **Data Collection:** Simulating context switch logs mapping Process ID -> System Call Stream.
2. **Feature Extractor:** Converts the streaming text (e.g., `read write execve ptrace`) into a numeric tensor (Vectorization).
3. **ML Inference Engine:** The loaded `RandomForestClassifier` processes the tensor within microseconds.
4. **Alerts System:** If probability > threshold (e.g., 60%), it logs an event pushed to the Flask dashboard via REST APIs causing the UI to flash RED.
