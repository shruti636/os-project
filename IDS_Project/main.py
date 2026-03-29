import argparse
import time
import random
from data_collection import generate_dataset, NORMAL_SYSCALLS, MALICIOUS_SYSCALLS
from model_training import train_model
from detector import RealTimeDetector
from utils import logger

def simulate_real_time_detection():
    detector = RealTimeDetector()
    logger.info("Starting real-time simulation...\n")
    
    # Simulate 10 process windows
    for i in range(1, 15):
        pid = random.randint(1000, 9999)
        
        # Decide if this window will be simulated as malicious or normal
        is_malicious = random.random() > 0.7 
        length = random.randint(20, 50)
        
        sequence = []
        if is_malicious:
            for _ in range(length):
                sequence.append(random.choice(MALICIOUS_SYSCALLS if random.random() > 0.3 else NORMAL_SYSCALLS))
        else:
            for _ in range(length):
                sequence.append(random.choice(NORMAL_SYSCALLS))
                
        syscall_str = " ".join(sequence)
        
        detector.analyze_syscall_window(pid, syscall_str)
        time.sleep(1.5) # Simulate delay

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine Learning IDS using Syscalls")
    parser.add_argument("--generate", action="store_true", help="Generate synthetic dataset")
    parser.add_argument("--train", action="store_true", help="Train the Random Forest model")
    parser.add_argument("--simulate", action="store_true", help="Run a live simulation of the detector")
    
    args = parser.parse_args()

    if args.generate:
        generate_dataset(num_samples=2000)
    elif args.train:
        train_model()
    elif args.simulate:
        simulate_real_time_detection()
    else:
        parser.print_help()
