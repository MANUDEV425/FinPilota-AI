"""
FinancePilot AI - ML Training Pipeline
Trains a Random Forest classifier on the UCI Default of Credit Card Clients dataset

Dataset: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
License: CC BY 4.0
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)
import joblib

# Configuration
RANDOM_SEED = 42
TEST_SIZE = 0.2
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'artifacts')
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls"
DATASET_LOCAL = os.path.join(os.path.dirname(__file__), '..', 'data', 'default_of_credit_card_clients.xls')

# Create artifacts directory
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

print("=" * 60)
print("FinancePilot AI - ML Training Pipeline")
print("=" * 60)

# Step 1: Load dataset
print("\n[1/6] Loading dataset...")
df = None

# Try local file first
if os.path.exists(DATASET_LOCAL):
    try:
        df = pd.read_excel(DATASET_LOCAL, skiprows=1)
        print(f"Dataset loaded from local file: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"Error loading local file: {e}")

# Try URL if local file not available
if df is None:
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        df = pd.read_excel(DATASET_URL, skiprows=1)
        print(f"Dataset loaded from URL: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"Error loading dataset from URL: {e}")
        print("\nAlternative: Download the dataset manually:")
        print("1. Visit: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients")
        print("2. Download the .xls file")
        print("3. Save it as: data/default_of_credit_card_clients.xls")
        print("4. Run training again")
        raise

if df is None:
    raise Exception("Failed to load dataset from both local file and URL")

# Step 2: Inspect and clean data
print("\n[2/6] Inspecting and cleaning data...")
print(f"Column names: {df.columns.tolist()}")

# Rename columns for clarity (based on dataset documentation)
column_mapping = {
    'ID': 'ID',
    'LIMIT_BAL': 'LIMIT_BAL',
    'SEX': 'SEX',
    'EDUCATION': 'EDUCATION',
    'MARRIAGE': 'MARRIAGE',
    'AGE': 'AGE',
    'PAY_0': 'PAY_0',
    'PAY_2': 'PAY_2',
    'PAY_3': 'PAY_3',
    'PAY_4': 'PAY_4',
    'PAY_5': 'PAY_5',
    'PAY_6': 'PAY_6',
    'BILL_AMT1': 'BILL_AMT1',
    'BILL_AMT2': 'BILL_AMT2',
    'BILL_AMT3': 'BILL_AMT3',
    'BILL_AMT4': 'BILL_AMT4',
    'BILL_AMT5': 'BILL_AMT5',
    'BILL_AMT6': 'BILL_AMT6',
    'PAY_AMT1': 'PAY_AMT1',
    'PAY_AMT2': 'PAY_AMT2',
    'PAY_AMT3': 'PAY_AMT3',
    'PAY_AMT4': 'PAY_AMT4',
    'PAY_AMT5': 'PAY_AMT5',
    'PAY_AMT6': 'PAY_AMT6',
    'default payment next month': 'default'
}

df = df.rename(columns=column_mapping)

# Remove ID column (identifier, not a feature)
if 'ID' in df.columns:
    df = df.drop('ID', axis=1)

print(f"Columns after cleaning: {df.columns.tolist()}")
print(f"Missing values: {df.isnull().sum().sum()}")

# Step 3: Define features and target
print("\n[3/6] Preparing features and target...")
target_column = 'default'

if target_column not in df.columns:
    raise ValueError(f"Target column '{target_column}' not found in dataset")

y = df[target_column]
X = df.drop(target_column, axis=1)

print(f"Target distribution:\n{y.value_counts()}")
print(f"Default rate: {y.mean():.2%}")

# Exclude demographic fields from features (for initial demo)
# Note: This does not guarantee fairness, but reduces direct demographic bias
demographic_columns = ['SEX', 'EDUCATION', 'MARRIAGE', 'AGE']
X_demographic = X[demographic_columns]
X = X.drop(demographic_columns, axis=1)

print(f"Features after excluding demographics: {X.columns.tolist()}")
print(f"Number of features: {X.shape[1]}")

# Step 4: Split data
print("\n[4/6] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=TEST_SIZE,
    random_state=RANDOM_SEED,
    stratify=y  # Stratified split to maintain class distribution
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"Training default rate: {y_train.mean():.2%}")
print(f"Test default rate: {y_test.mean():.2%}")

# Step 5: Train model
print("\n[5/6] Training Random Forest model...")
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        class_weight='balanced'  # Handle class imbalance
    ))
])

pipeline.fit(X_train, y_train)
print("Model training completed")

# Step 6: Evaluate model
print("\n[6/6] Evaluating model...")
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)[:, 1]

# Calculate metrics
metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision_default': precision_score(y_test, y_pred, pos_label=1),
    'recall_default': recall_score(y_test, y_pred, pos_label=1),
    'f1_score': f1_score(y_test, y_pred, pos_label=1),
    'roc_auc': roc_auc_score(y_test, y_pred_proba),
    'average_precision': average_precision_score(y_test, y_pred_proba),
}

print("\nEvaluation Metrics:")
for metric, value in metrics.items():
    print(f"  {metric}: {value:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:\n{cm}")

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pipeline.named_steps['classifier'].feature_importances_
feature_names = X.columns.tolist()
importance_dict = dict(zip(feature_names, feature_importance))

print("\nTop 10 Feature Importances:")
sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
for feature, importance in sorted_features[:10]:
    print(f"  {feature}: {importance:.4f}")

# Step 7: Save artifacts
print("\nSaving artifacts...")

# Save model
model_path = os.path.join(ARTIFACTS_DIR, 'model.joblib')
joblib.dump(pipeline, model_path)
print(f"Model saved to: {model_path}")

# Save metrics
metrics_path = os.path.join(ARTIFACTS_DIR, 'metrics.json')
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"Metrics saved to: {metrics_path}")

# Save feature importance
importance_path = os.path.join(ARTIFACTS_DIR, 'feature_importance.json')
with open(importance_path, 'w') as f:
    json.dump(importance_dict, f, indent=2)
print(f"Feature importance saved to: {importance_path}")

# Save feature schema
schema_path = os.path.join(ARTIFACTS_DIR, 'feature_schema.json')
schema = {
    'features': feature_names,
    'target': target_column,
    'demographic_excluded': demographic_columns,
    'n_features': len(feature_names),
    'random_seed': RANDOM_SEED,
}
with open(schema_path, 'w') as f:
    json.dump(schema, f, indent=2)
print(f"Feature schema saved to: {schema_path}")

# Save demo sample (from test set)
demo_sample = X_test.iloc[0].to_dict()
demo_path = os.path.join(ARTIFACTS_DIR, 'demo_sample.json')
with open(demo_path, 'w') as f:
    json.dump(demo_sample, f, indent=2)
print(f"Demo sample saved to: {demo_path}")

# Save demo sample true label (separate from features)
demo_label = int(y_test.iloc[0])
demo_label_path = os.path.join(ARTIFACTS_DIR, 'demo_label.json')
with open(demo_label_path, 'w') as f:
    json.dump({'true_label': demo_label}, f)
print(f"Demo label saved to: {demo_label_path}")

# Save metadata
metadata = {
    'model_type': 'RandomForestClassifier',
    'model_version': 'v1',
    'dataset': 'UCI Default of Credit Card Clients',
    'dataset_url': 'https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients',
    'license': 'CC BY 4.0',
    'training_date': pd.Timestamp.now().isoformat(),
    'n_samples': len(df),
    'n_features': len(feature_names),
    'random_seed': RANDOM_SEED,
    'test_size': TEST_SIZE,
    'limitations': [
        'Historical Taiwanese dataset from 2005',
        'Not validated for Indian borrowers',
        'Not a model of company financial health',
        'Demographic fields excluded from training but this does not guarantee fairness',
        'Model probabilities are uncalibrated',
        'For demonstration and educational purposes only',
    ],
}

metadata_path = os.path.join(ARTIFACTS_DIR, 'metadata.json')
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"Metadata saved to: {metadata_path}")

print("\n" + "=" * 60)
print("Training pipeline completed successfully!")
print("=" * 60)
print(f"\nAll artifacts saved to: {ARTIFACTS_DIR}")
print("\nIMPORTANT: Model limitations must be disclosed in production use.")
