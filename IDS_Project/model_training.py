import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from feature_extraction import SyscallFeatureExtractor
from utils import logger, ensure_dirs

def train_model(dataset_path="data/dataset.csv", model_path="models/rf_model.pkl", extractor_path="models/extractor.pkl"):
    ensure_dirs()

    if not os.path.exists(dataset_path):
        logger.error(f"Dataset {dataset_path} not found. Please generate it first.")
        return

    logger.info("Loading dataset...")
    df = pd.read_csv(dataset_path)
    X_raw = df['sequence'].values
    y = df['label'].values

    logger.info("Extracting features (N-grams)...")
    extractor = SyscallFeatureExtractor(ngram_range=(1, 2), max_features=300)
    X = extractor.fit_transform(X_raw)

    # Train-test split
    logger.info("Splitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Model training
    logger.info("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=15)
    model.fit(X_train, y_train)

    # Evaluation
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    logger.info(f"\nModel Performance Metrics:")
    logger.info(f"Accuracy:  {acc:.4f}")
    logger.info(f"Precision: {prec:.4f}")
    logger.info(f"Recall:    {rec:.4f}")
    logger.info(f"F1 Score:  {f1:.4f}")
    logger.info(f"\nConfusion Matrix:\n{cm}")
    logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

    # Save models
    logger.info("Saving model and extractor...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(extractor_path, 'wb') as f:
        pickle.dump(extractor, f)

    logger.info("Training Complete! Models saved to 'models/' directory.")

if __name__ == "__main__":
    train_model()
