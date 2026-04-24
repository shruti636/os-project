import argparse
from data_collection import generate_real_dataset
from model_training import train_model
from utils import logger

def execute_pipeline():
    logger.info("--- Phase 1: Gathering REAL Os Traces ---")
    generate_real_dataset(duration_per_class=10)
    logger.info("--- Phase 2: Neural Engine Training ---")
    train_model(dataset_path="data/dataset.csv")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true", help="Harvest real dataset")
    parser.add_argument("--train", action="store_true", help="Train the model")
    
    args = parser.parse_args()

    if args.generate:
        generate_real_dataset(duration_per_class=15)
    elif args.train:
        train_model()
    else:
        # If no arguments provided, just do both to be extremely helpful
        execute_pipeline()
