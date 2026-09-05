"""
NutriAI — Hybrid Recommendation Engine
Lead ML Engineer: Romina Koju (790332)
Backend Integration: Prashant Ghimire (790328)

Formula:
  Final Score = 0.50 * ML_Quality + 0.30 * Budget_Fit + 0.20 * Behavioral_Preference

Safety Guarantee:
  Allergens & dietary restrictions are filtered strictly beforehand (hard exclusion).
"""

import os
from pathlib import Path
import joblib
import numpy as np
from django.utils import timezone

from myapp.models import Food, RecommendationHistory, UserProfile
from myapp.services.calculations import calculate_daily_summary, calculate_daily_targets
from myapp.ml.dataset import compute_nutritional_score

MODEL_PATH = Path(__file__).resolve().parent / "models" / "xgboost_recommender.joblib"
_CACHED_MODEL = None


def _get_ml_model():
    global _CACHED_MODEL
    if _CACHED_MODEL is None and MODEL_PATH.exists():
        try:
            _CACHED_MODEL = joblib.load(MODEL_PATH)
        except Exception:
            _CACHED_MODEL = None
    return _CACHED_MODEL


def cosine_similarity(v1, v2):
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-7 or norm2 < 1e-7:
        return 0.5
    return float(np.clip(np.dot(v1, v2) / (norm1 * norm2), 0.0, 1.0))


def compute_budget_fit(food, daily_summary):
    """
    Evaluates how well a food fits the user's remaining calorie & macro budget for today.
    """
    cal_target = daily_summary["targets"]["calorie_target"]
    rem_cal = daily_summary["remaining_calories"]
    rem_prot = daily_summary["remaining_protein"]
    rem_carb = daily_summary["remaining_carbohydrates"]
    rem_fat = daily_summary["remaining_fat"]
    over_budget = daily_summary["over_budget"]

    food_cal = float(food.calories or 0)
    food_prot = float(food.protein or 0)
    food_carb = float(food.carbohydrates or 0)
    food_fat = float(food.fat or 0)

    if over_budget or rem_cal <= 100:
        # Over-budget branch: heavily favor low-calorie, nutrient-dense foods (e.g. Gundruk, light soups)
        if food_cal <= 120:
            return 0.95
        elif food_cal <= 200:
            return 0.70
        else:
            return max(0.1, 1.0 - (food_cal / 600.0))

    # Normal budget fit: macro balance alignment using vector similarity
    target_macro_vector = np.array([rem_prot * 4.0, rem_carb * 4.0, rem_fat * 9.0])
    food_macro_vector = np.array([food_prot * 4.0, food_carb * 4.0, food_fat * 9.0])

    macro_sim = cosine_similarity(target_macro_vector, food_macro_vector)

    # Calorie proximity penalty: ideally a single meal occupies 25% to 40% of daily target
    ideal_meal_cal = max(200.0, min(rem_cal, cal_target * 0.35))
    cal_diff_ratio = abs(food_cal - ideal_meal_cal) / ideal_meal_cal
    cal_fit = float(np.clip(1.0 - (0.5 * cal_diff_ratio), 0.1, 1.0))

    budget_score = (0.60 * cal_fit) + (0.40 * macro_sim)
    return float(np.clip(budget_score, 0.0, 1.0))


def get_behavioral_score(user, food):
    """
    Computes a bonus or penalty based on past interactions with this food.
    """
    history_entries = RecommendationHistory.objects.filter(
        user=user,
        food=food
    ).order_by("-recommended_at")[:5]

    if not history_entries.exists():
        return 0.5  # Neutral default

    score = 0.5
    for h in history_entries:
        if h.is_eaten:
            score += 0.15
        if h.user_rating is not None:
            if h.user_rating >= 4:
                score += 0.20
            elif h.user_rating <= 2:
                score -= 0.25

    return float(np.clip(score, 0.0, 1.0))


def get_recommendations(user, limit=6, meal_type=None):
    """
    Returns personalized Nepali food recommendations for the given user.

    Steps:
      1. Pre-filtering: strict safety filter on allergens and dietary restrictions.
      2. XGBoost regression model prediction for nutritional quality score.
      3. Budget fit calculation based on remaining daily calories & macros.
      4. Behavioral score from user interaction history.
      5. Hybrid weighted combination & ranking.
    """
    profile = getattr(user, "userprofile", None)
    if not profile:
        profile, _ = UserProfile.objects.get_or_create(user=user)

    # Start with all available foods
    queryset = Food.objects.all().prefetch_related("allergens", "dietary_tags", "category")

    # -------------------------------------------------------------
    # 1. HARD SAFETY FILTERS (Allergens & Preferences)
    # -------------------------------------------------------------
    ALLERGY_SYNONYMS = {
        "dairy": ["Milk"],
        "lactose": ["Milk"],
        "milk": ["Milk"],
        "peanut": ["Peanuts"],
        "peanuts": ["Peanuts"],
        "tree nut": ["Tree Nuts"],
        "tree nuts": ["Tree Nuts"],
        "nut": ["Tree Nuts", "Peanuts"],
        "nuts": ["Tree Nuts", "Peanuts"],
        "gluten": ["Gluten", "Wheat"],
        "wheat": ["Wheat", "Gluten"],
        "egg": ["Eggs"],
        "eggs": ["Eggs"],
        "soy": ["Soy"],
        "fish": ["Fish", "Shellfish"],
    }

    raw_allergies = list(profile.allergies.values_list("name", flat=True))
    if profile.custom_allergies:
        raw_allergies.extend([a.strip() for a in profile.custom_allergies.split(",") if a.strip()])

    # Expand allergen synonyms into a comprehensive set
    active_allergens = set()
    for a in raw_allergies:
        a_clean = a.strip()
        active_allergens.add(a_clean)
        for syn_key, mapped_list in ALLERGY_SYNONYMS.items():
            if syn_key in a_clean.lower():
                active_allergens.update(mapped_list)

    # Exclude any food with overlapping allergens
    if active_allergens:
        queryset = queryset.exclude(allergens__name__in=list(active_allergens))

    # Dietary preferences
    user_diet_tags = list(profile.dietary_tags.values_list("name", flat=True))
    if profile.custom_dietary_tags:
        user_diet_tags.extend([t.strip() for t in profile.custom_dietary_tags.split(",") if t.strip()])

    is_veg = any("veg" in t.lower() for t in user_diet_tags)
    is_vegan = any("vegan" in t.lower() for t in user_diet_tags)
    is_gf = any("gluten" in t.lower() for t in user_diet_tags)

    if is_vegan:
        queryset = queryset.filter(dietary_tags__name__iexact="Vegan")
    elif is_veg:
        queryset = queryset.filter(dietary_tags__name__iexact="Vegetarian")

    if is_gf:
        queryset = queryset.filter(dietary_tags__name__iexact="Gluten Free").exclude(allergens__name__in=["Gluten", "Wheat"])

    foods = list(queryset.distinct())
    if not foods:
        # Graceful fallback that STILL strictly respects allergen safety
        fallback_qs = Food.objects.all()
        if active_allergens:
            fallback_qs = fallback_qs.exclude(allergens__name__in=list(active_allergens))
        if is_veg or is_vegan:
            fallback_qs = fallback_qs.filter(dietary_tags__name__iexact="Vegetarian")
        foods = list(fallback_qs.distinct()[:10])

    daily_summary = calculate_daily_summary(user, profile)
    model = _get_ml_model()

    scored_items = []

    for food in foods:
        cal = float(food.calories or 0)
        prot = float(food.protein or 0)
        carb = float(food.carbohydrates or 0)
        fat = float(food.fat or 0)
        fib = float(food.fiber or 0)
        sug = float(food.sugar or 0)
        sod = float(food.sodium or 0)

        # 2. ML Quality Score
        if model is not None:
            feats = np.array([[cal, prot, carb, fat, fib, sug, sod]], dtype=np.float32)
            ml_score = float(np.clip(model.predict(feats)[0], 0.0, 1.0))
        else:
            ml_score = compute_nutritional_score(cal, prot, carb, fat, fib, sug, sod)

        # 3. Budget Fit Score
        budget_score = compute_budget_fit(food, daily_summary)

        # 4. Behavioral Score
        behavior_score = get_behavioral_score(user, food)

        # 5. Hybrid Final Score (50% ML + 30% Budget + 20% Behavior)
        final_score = (0.50 * ml_score) + (0.30 * budget_score) + (0.20 * behavior_score)
        match_pct = int(round(final_score * 100))

        # Generate contextual rationale badges
        reasons = []
        if prot >= 15:
            reasons.append("High Protein")
        if fib >= 5:
            reasons.append("Fiber Rich")
        if food.is_nepali:
            reasons.append("Nepali Cuisine")
        if cal <= 200:
            reasons.append("Low Calorie")
        elif cal >= 450:
            reasons.append("Hearty Staple")

        scored_items.append({
            "food": food,
            "score": round(final_score, 4),
            "ml_score": round(ml_score, 3),
            "budget_score": round(budget_score, 3),
            "match_pct": match_pct,
            "reasons": reasons[:3],
        })

    # Sort descending by final score
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    recommendations = scored_items[:limit]

    # Record recommendations in RecommendationHistory for tracking & behavioral feedback loop
    for item in recommendations:
        RecommendationHistory.objects.create(
            user=user,
            food=item["food"],
            score=item["score"],
            ml_score=item["ml_score"],
            budget_fit_score=item["budget_score"],
        )

    return recommendations
