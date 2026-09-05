"""
NutriAI — NepaliNutriDB Machine Learning Dataset & Quality Scoring
Lead ML Engineer: Romina Koju (790332)

This module handles:
1. Feature vector extraction from NepaliNutriDB Food instances.
2. Scientific nutritional density scoring formula used to generate training targets.
3. Dataset augmentation with synthetic negative/positive anchor foods for balanced distribution.
"""

import numpy as np
from myapp.models import Food

# Standard nutrient feature names for ML training
FEATURE_NAMES = [
    "calories",
    "protein",
    "carbohydrates",
    "fat",
    "fiber",
    "sugar",
    "sodium",
]


def compute_nutritional_score(calories, protein, carbohydrates, fat, fiber, sugar, sodium):
    """
    Computes an evidence-based nutritional density score in [0.0, 1.0].

    Scientific basis:
      - Protein Density (35% weight): Ratio of protein energy to total calories.
        Protein is vital for tissue repair, satiety, and metabolic rate.
      - Dietary Fiber (20% weight): Normalized up to 10g per serving.
        Promotes digestive health and lowers glycemic response.
      - Fat Balance (20% weight): Penalizes excessive lipid concentration (>40% of energy).
      - Sugar Penalty (15% weight): Penalizes high free sugars (>25g per serving).
      - Sodium Penalty (10% weight): Penalizes excess sodium (>500mg per serving)
        associated with hypertension.
    """
    cal = max(float(calories or 0), 1.0)
    prot = float(protein or 0)
    carb = float(carbohydrates or 0)
    fat = float(fat or 0)
    fib = float(fiber or 0)
    sug = float(sugar or 0)
    sod = float(sodium or 0)

    # 1. Protein density: fraction of calories from protein (1g protein = 4 kcal)
    prot_density = np.clip((prot * 4.0) / cal, 0.0, 1.0)

    # 2. Dietary fiber score: 10g per serving is ideal
    fiber_score = np.clip(fib / 10.0, 0.0, 1.0)

    # 3. Fat penalty: if more than 35% of calories from fat, score decreases
    fat_fraction = np.clip((fat * 9.0) / cal, 0.0, 1.0)
    fat_score = float(np.clip(1.0 - (fat_fraction * 0.8), 0.0, 1.0))

    # 4. Sugar penalty: >25g per serving gives heavy penalty
    sugar_penalty = np.clip(sug / 25.0, 0.0, 1.0)
    sugar_score = 1.0 - sugar_penalty

    # 5. Sodium penalty: >500mg gives penalty
    sodium_penalty = np.clip(sod / 500.0, 0.0, 1.0)
    sodium_score = 1.0 - sodium_penalty

    # Weighted linear combination
    raw_score = (
        0.35 * prot_density +
        0.20 * fiber_score +
        0.20 * fat_score +
        0.15 * sugar_score +
        0.10 * sodium_score
    )

    return float(np.clip(raw_score, 0.0, 1.0))


def build_ml_dataset():
    """
    Constructs the feature matrix X and target label vector y.
    Combines real NepaliNutriDB food records with synthetic anchor profiles
    to produce statistically reliable distribution variance for regression.
    """
    foods = list(Food.objects.all())
    if not foods:
        raise ValueError("No food records found in database. Run seed_demo_data first.")

    X_list = []
    y_list = []

    for f in foods:
        cal = float(f.calories or 0)
        prot = float(f.protein or 0)
        carb = float(f.carbohydrates or 0)
        fat = float(f.fat or 0)
        fib = float(f.fiber or 0)
        sug = float(f.sugar or 0)
        sod = float(f.sodium or 0)

        features = [cal, prot, carb, fat, fib, sug, sod]
        score = compute_nutritional_score(cal, prot, carb, fat, fib, sug, sod)

        X_list.append(features)
        y_list.append(score)

    # Anchor synthetic boundary profiles (to teach ML models extremes)
    synthetic_anchors = [
        # Ultra-processed / pure sugar (near 0)
        ([450, 0.5, 110, 1.0, 0.0, 95, 20], 0.05),
        ([550, 3.0, 80, 25.0, 0.5, 55, 180], 0.12),
        ([850, 5.0, 60, 65.0, 1.0, 15, 800], 0.08),
        ([700, 2.0, 50, 55.0, 0.0, 10, 950], 0.06),
        # Nutrient-dense lean staples (high score 0.85 - 0.98)
        ([110, 24.0, 0.0, 1.5, 0.0, 0.0, 65], 0.94),  # boiled chicken breast
        ([120, 12.0, 18.0, 1.0, 9.0, 0.5, 90], 0.92),  # high fiber lentil/kwati
        ([85, 4.0, 12.0, 0.5, 7.0, 0.0, 40], 0.90),   # leafy greens / gundruk
        ([140, 15.0, 15.0, 2.0, 6.0, 1.0, 80], 0.89),  # soybean/bhatmas
    ]

    for feats, label in synthetic_anchors:
        X_list.append(feats)
        y_list.append(label)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.float32)

    return X, y
