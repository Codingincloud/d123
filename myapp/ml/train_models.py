"""
NutriAI — ML Recommendation Model Training & Evaluation Pipeline
Lead ML Engineer: Romina Koju (790332)

Trains two models on NepaliNutriDB:
1. Primary Model: XGBoost Regressor (Extreme Gradient Boosting)
2. Benchmark Model: Random Forest Regressor

Run from project root:
    python myapp/ml/train_models.py
"""

import os
import sys
from pathlib import Path

# Setup Django standalone execution if called directly
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nutriai.settings")
import django
django.setup()

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from myapp.ml.dataset import FEATURE_NAMES, build_ml_dataset


def train_models():
    print("=" * 60)
    print("NutriAI — Training Recommendation Models on NepaliNutriDB")
    print("=" * 60)

    # 1. Load dataset
    X, y = build_ml_dataset()
    print(f"Total dataset samples: {X.shape[0]} (Features: {X.shape[1]})")

    # 2. Train-Test Split (80% train, 20% test, random_state=42 for reproducibility)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

    # 3. Model 1: XGBoost Regressor (Primary)
    print("\nTraining XGBoost Regressor (Primary)...")
    xgb_model = XGBRegressor(
        n_estimators=120,
        learning_rate=0.08,
        max_depth=4,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
    )
    xgb_model.fit(X_train, y_train)
    xgb_pred = xgb_model.predict(X_test)

    # 4. Model 2: Random Forest Regressor (Benchmark)
    print("Training Random Forest Regressor (Benchmark)...")
    rf_model = RandomForestRegressor(
        n_estimators=120,
        max_depth=6,
        random_state=42,
    )
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)

    # 5. Evaluate both models
    def get_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        # Binarized suitability (score >= 0.50 is healthy recommendation)
        y_true_bin = (y_true >= 0.50).astype(int)
        y_pred_bin = (y_pred >= 0.50).astype(int)

        acc = accuracy_score(y_true_bin, y_pred_bin)
        prec = precision_score(y_true_bin, y_pred_bin, zero_division=0)
        rec = recall_score(y_true_bin, y_pred_bin, zero_division=0)
        f1 = f1_score(y_true_bin, y_pred_bin, zero_division=0)

        return {
            "R2": r2,
            "MAE": mae,
            "RMSE": rmse,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1": f1,
        }

    xgb_metrics = get_metrics(y_test, xgb_pred)
    rf_metrics = get_metrics(y_test, rf_pred)

    # 6. Print Comparison Table
    print("\n" + "=" * 65)
    print("           MODEL PERFORMANCE COMPARISON ON NEPALI NUTRIDB")
    print("=" * 65)
    print(f"{'Metric':<18} | {'XGBoost (Primary)':<18} | {'Random Forest':<18}")
    print("-" * 65)
    print(f"{'R² Score':<18} | {xgb_metrics['R2']:<18.4f} | {rf_metrics['R2']:<18.4f}")
    print(f"{'MAE':<18} | {xgb_metrics['MAE']:<18.4f} | {rf_metrics['MAE']:<18.4f}")
    print(f"{'RMSE':<18} | {xgb_metrics['RMSE']:<18.4f} | {rf_metrics['RMSE']:<18.4f}")
    print(f"{'Binary Accuracy':<18} | {xgb_metrics['Accuracy']:<18.4f} | {rf_metrics['Accuracy']:<18.4f}")
    print(f"{'Precision':<18} | {xgb_metrics['Precision']:<18.4f} | {rf_metrics['Precision']:<18.4f}")
    print(f"{'Recall':<18} | {xgb_metrics['Recall']:<18.4f} | {rf_metrics['Recall']:<18.4f}")
    print(f"{'F1 Score':<18} | {xgb_metrics['F1']:<18.4f} | {rf_metrics['F1']:<18.4f}")
    print("=" * 65)

    # 7. Feature Importance (XGBoost)
    importances = xgb_model.feature_importances_
    print("\nXGBoost Feature Importances:")
    for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True):
        print(f"  - {name:<15}: {imp:.4f} ({imp * 100:.1f}%)")

    # 8. Save models
    models_dir = Path(__file__).resolve().parent / "models"
    models_dir.mkdir(exist_ok=True, parents=True)

    xgb_path = models_dir / "xgboost_recommender.joblib"
    rf_path = models_dir / "rf_recommender.joblib"

    joblib.dump(xgb_model, xgb_path)
    joblib.dump(rf_model, rf_path)

    print(f"\nSaved XGBoost model to: {xgb_path}")
    print(f"Saved Random Forest model to: {rf_path}")

    # 9. Generate Markdown report for defense documentation
    report_path = Path(__file__).resolve().parent / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# NutriAI — Machine Learning Evaluation Report\n\n")
        f.write("**Lead ML Engineer:** Romina Koju (790332)\n")
        f.write(f"**Dataset:** NepaliNutriDB ({X.shape[0]} samples, {X.shape[1]} features)\n\n")
        f.write("## Model Performance Comparison\n\n")
        f.write("| Metric | XGBoost (Primary) | Random Forest (Benchmark) |\n")
        f.write("|---|---|---|\n")
        f.write(f"| **R² Score** | {xgb_metrics['R2']:.4f} | {rf_metrics['R2']:.4f} |\n")
        f.write(f"| **MAE** | {xgb_metrics['MAE']:.4f} | {rf_metrics['MAE']:.4f} |\n")
        f.write(f"| **RMSE** | {xgb_metrics['RMSE']:.4f} | {rf_metrics['RMSE']:.4f} |\n")
        f.write(f"| **Binary Accuracy** | {xgb_metrics['Accuracy'] * 100:.2f}% | {rf_metrics['Accuracy'] * 100:.2f}% |\n")
        f.write(f"| **Precision** | {xgb_metrics['Precision']:.4f} | {rf_metrics['Precision']:.4f} |\n")
        f.write(f"| **Recall** | {xgb_metrics['Recall']:.4f} | {rf_metrics['Recall']:.4f} |\n")
        f.write(f"| **F1 Score** | {xgb_metrics['F1']:.4f} | {rf_metrics['F1']:.4f} |\n\n")
        f.write("## Feature Importances (XGBoost)\n\n")
        for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True):
            f.write(f"- **{name.capitalize()}**: {imp * 100:.1f}%\n")

    print(f"Saved evaluation report to: {report_path}")
    return xgb_metrics


if __name__ == "__main__":
    train_models()
