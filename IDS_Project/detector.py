import pickle
import os
import time
from collections import deque
from utils import logger

class RealTimeDetector:
    def __init__(self, model_path="models/rf_model.pkl", extractor_path="models/extractor.pkl"):
        """Initialize the real-time detector by loading the model and extractor."""
        if not os.path.exists(model_path) or not os.path.exists(extractor_path):
            raise FileNotFoundError("Model files not found. Please train the model first.")

        logger.info("Loading Intrusion Detection Model...")
        with open(model_path, 'rb') as mf:
            self.model = pickle.load(mf)

        logger.info("Loading Feature Extractor...")
        with open(extractor_path, 'rb') as ef:
            self.extractor = pickle.load(ef)

        self.alert_history = deque(maxlen=100) # Store last 100 alerts for UI/Logs
        logger.info("Real-Time Detector Initialized Successfully.")

    def analyze_syscall_window(self, process_id, syscall_sequence):
        """
        Analyze a window of system calls in real-time.
        :param process_id: ID of the process being monitored
        :param syscall_sequence: String of spaced system calls 
        :return: (prediction, probability)
        """
        # Feature extraction
        try:
            features = self.extractor.transform([syscall_sequence])

            # Predict
            prob = self.model.predict_proba(features)[0]
            malicious_prob = prob[1]

            # Threshold for alert
            status = "MALICIOUS" if malicious_prob > 0.6 else "SAFE"

            # Formatting event
            event = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "pid": process_id,
                "status": status,
                "confidence": round(malicious_prob * 100, 2),
                "sequence_preview": syscall_sequence[:30] + "..."
            }

            self.alert_history.append(event)

            if status == "MALICIOUS":
                logger.warning(f"[🚨 ALERT] PID {process_id} flagged as MALICIOUS! Confidence: {event['confidence']}%")
            else:
                logger.info(f"[✅ SAFE] PID {process_id} behaves normally. Confidence: {100-event['confidence']}%")

            return event

        except Exception as e:
            logger.error(f"Error analyzing window: {e}")
            return None
