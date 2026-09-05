# NutriAI — Machine Learning Evaluation Report

**Lead ML Engineer:** Romina Koju (790332)
**Dataset:** NepaliNutriDB (137 samples, 7 features)

## Model Performance Comparison

| Metric | XGBoost (Primary) | Random Forest (Benchmark) |
|---|---|---|
| **R² Score** | 0.7615 | 0.5858 |
| **MAE** | 0.0358 | 0.0456 |
| **RMSE** | 0.0707 | 0.0931 |
| **Binary Accuracy** | 92.86% | 89.29% |
| **Precision** | 1.0000 | 1.0000 |
| **Recall** | 0.6667 | 0.5000 |
| **F1 Score** | 0.8000 | 0.6667 |

## Feature Importances (XGBoost)

- **Fiber**: 38.4%
- **Sugar**: 26.7%
- **Fat**: 9.7%
- **Carbohydrates**: 7.7%
- **Calories**: 6.7%
- **Protein**: 6.1%
- **Sodium**: 4.7%
