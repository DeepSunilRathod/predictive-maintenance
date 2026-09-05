"""
Training script for the fault-classification model.

*** THIS PROJECT SHIPS WITHOUT A TRAINED MODEL. ***
No labeled fault dataset for your actual motor exists yet, so we are not
going to train a model on synthetic data and pretend it's meaningful -
that would produce fake confidence and fake accuracy claims, which the
project spec explicitly forbids.

Once you have collected labeled data (rows of temperature/current/vibration/
rpm together with a known condition label - e.g. from run-to-failure tests,
manually logged faults, or a public bearing-fault dataset such as CWRU),
put it in ml/data/labeled_dataset.csv with columns:

    temperature,current,vibration,rpm,label

...where label is one of:
    Normal, Overheating, Overcurrent, Excessive_Vibration,
    Underspeed_Overspeed, Bearing_Abnormality, Multiple_Abnormality

Then run:
    cd backend
    python -m ml.train_model

This will train a scikit-learn classifier (RandomForest by default),
report a real held-out accuracy score, and save it to ml/model.pkl.
predict.py will automatically pick it up.
"""
import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from ml.preprocessing import FEATURE_ORDER

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "labeled_dataset.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def main():
    if not os.path.exists(DATA_PATH):
        print(f"No labeled dataset found at {DATA_PATH}.")
        print("Training was skipped - the API will keep reporting 'model not available'")
        print("until you add real labeled data and re-run this script. See the docstring")
        print("at the top of this file for the required CSV format.")
        sys.exit(0)

    df = pd.read_csv(DATA_PATH)
    missing = [c for c in FEATURE_ORDER + ["label"] if c not in df.columns]
    if missing:
        print(f"Dataset is missing required columns: {missing}")
        sys.exit(1)

    X = df[FEATURE_ORDER]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Held-out test accuracy: {acc:.3f}")
    print(classification_report(y_test, y_pred))

    joblib.dump({"model": model, "feature_order": FEATURE_ORDER, "test_accuracy": acc}, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
