import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

data_path = DATA_DIR / "historical_shipments.csv"

df = pd.read_csv(data_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# ============================================================
# FEATURES
# ============================================================

features = [
    "Distance_KM",
    "Carrier",
    "Vehicle_ID",
    "Load_KG",
    "Traffic",
    "Weather",
    "Priority",
    "Delivery_Window_Hours"
]

target = "Delayed"

X = df[features]
y = df[target]


# ============================================================
# CATEGORICAL AND NUMERICAL FEATURES
# ============================================================

categorical_features = [
    "Carrier",
    "Vehicle_ID",
    "Traffic",
    "Weather",
    "Priority"
]

numerical_features = [
    "Distance_KM",
    "Load_KG",
    "Delivery_Window_Hours"
]


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# Transform data
X_processed = preprocessor.fit_transform(X)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X_processed,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_probability)

print("\n===================================")
print("      LOGIOPT AI MODEL RESULTS")
print("===================================")

print(f"\nAccuracy : {accuracy:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# ============================================================
# SAVE MODEL
# ============================================================

model_path = MODEL_DIR / "logiopt_delay_model.pkl"
preprocessor_path = MODEL_DIR / "logiopt_preprocessor.pkl"

joblib.dump(model, model_path)
joblib.dump(preprocessor, preprocessor_path)


print("\n===================================")
print("Models saved successfully!")
print("===================================")

print(f"\nModel:")
print(model_path)

print("\nPreprocessor:")
print(preprocessor_path)