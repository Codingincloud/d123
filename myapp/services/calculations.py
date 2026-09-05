from datetime import date


def calculate_age(date_of_birth):
    if not date_of_birth:
        return None

    today = date.today()

    age = today.year - date_of_birth.year

    if (today.month, today.day) < (
        date_of_birth.month,
        date_of_birth.day
    ):
        age -= 1

    return age


def calculate_bmr(
    weight,
    height,
    age,
    gender
):
    if not weight or not height or not age or not gender:
        return None

    try:
        w = float(weight)
        h = float(height)
        a = float(age)
    except (ValueError, TypeError):
        return None

    g = str(gender).strip().lower()
    if g in ("male", "m"):
        bmr = 10 * w + 6.25 * h - 5 * a + 5
    elif g in ("female", "f"):
        bmr = 10 * w + 6.25 * h - 5 * a - 161
    else:
        # Default gender-neutral average
        bmr = 10 * w + 6.25 * h - 5 * a - 78

    return round(bmr)


def calculate_tdee(
    bmr,
    activity_level
):
    if not bmr or not activity_level:
        return None

    act = str(activity_level).strip().lower()
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "lightly active": 1.375,
        "moderate": 1.55,
        "moderately active": 1.55,
        "very": 1.725,
        "very active": 1.725,
        "active": 1.725,
        "extra": 1.9,
    }

    multiplier = activity_multipliers.get(act, 1.2)
    return round(float(bmr) * multiplier)


def calculate_nutrition_baseline(profile):
    """
    Calculate the user's basic nutrition metrics (BMR & TDEE)
    using the scientific Mifflin-St Jeor equation.
    """
    if not profile:
        return None

    age = calculate_age(profile.date_of_birth)
    if age is None:
        age = 25  # Sensible default if DOB not provided

    bmr = calculate_bmr(
        weight=profile.weight,
        height=profile.height,
        age=age,
        gender=profile.gender
    )
    tdee = calculate_tdee(
        bmr=bmr,
        activity_level=profile.activity_level
    )

    return {
        "age": age,
        "bmr": bmr,
        "tdee": tdee,
    }


def calculate_daily_targets(profile):
    """
    Calculate goal-adjusted daily calorie and macronutrient targets.

    Formulas:
      - Lose Weight: TDEE - 500 kcal (safe 0.5kg/week deficit, floor 1200 kcal)
      - Gain Weight: TDEE + 500 kcal (surplus for lean mass)
      - Maintain: TDEE
    Macronutrient splits:
      - Standard / Lose: 25% Protein, 50% Carbs, 25% Fat
      - Gain: 30% Protein, 45% Carbs, 25% Fat
      - Fiber: 30g daily standard
    """
    if not profile:
        return {
            "calorie_target": 2000,
            "target_protein": 125.0,
            "target_carbohydrates": 250.0,
            "target_fat": 55.6,
            "target_fiber": 30.0,
            "target_water": 2500,
        }

    baseline = calculate_nutrition_baseline(profile)
    tdee = baseline["tdee"] if baseline and baseline["tdee"] else 2000

    # User override or goal-adjusted calculation
    if profile.daily_calorie_target and profile.daily_calorie_target > 500:
        calorie_target = float(profile.daily_calorie_target)
    else:
        goal = (profile.goal or "maintain").strip().lower()
        if "lose" in goal:
            calorie_target = max(1200.0, float(tdee) - 500.0)
        elif "gain" in goal:
            calorie_target = float(tdee) + 500.0
        else:
            calorie_target = float(tdee)

    calorie_target = round(calorie_target)

    # Goal-tailored macro distribution
    goal_str = (profile.goal or "maintain").strip().lower()
    if "gain" in goal_str:
        target_protein = round((calorie_target * 0.30) / 4.0, 1)
        target_carbs = round((calorie_target * 0.45) / 4.0, 1)
        target_fat = round((calorie_target * 0.25) / 9.0, 1)
    else:
        target_protein = round((calorie_target * 0.25) / 4.0, 1)
        target_carbs = round((calorie_target * 0.50) / 4.0, 1)
        target_fat = round((calorie_target * 0.25) / 9.0, 1)

    target_fiber = 30.0
    target_water = round(float(profile.weight) * 35) if profile.weight else 2500

    return {
        "calorie_target": calorie_target,
        "target_protein": target_protein,
        "target_carbohydrates": target_carbs,
        "target_fat": target_fat,
        "target_fiber": target_fiber,
        "target_water": target_water,
    }


def calculate_daily_summary(user, profile=None):
    """
    Compute total consumed vs remaining nutrition budget for today.
    """
    from django.utils import timezone
    from myapp.models import MealLog, WaterLog

    if profile is None and hasattr(user, "userprofile"):
        profile = user.userprofile

    targets = calculate_daily_targets(profile)
    today = timezone.localdate()

    today_meals = MealLog.objects.filter(
        user=user,
        consumed_at__date=today
    )

    consumed_calories = sum(m.calories for m in today_meals)
    consumed_protein = sum(m.protein for m in today_meals)
    consumed_carbs = sum(m.carbohydrates for m in today_meals)
    consumed_fat = sum(m.fat for m in today_meals)
    consumed_fiber = sum(m.fiber for m in today_meals)

    today_water_logs = WaterLog.objects.filter(
        user=user,
        consumed_at__date=today
    )
    consumed_water = sum(w.amount_ml for w in today_water_logs)

    cal_target = targets["calorie_target"]
    prot_target = targets["target_protein"]
    carb_target = targets["target_carbohydrates"]
    fat_target = targets["target_fat"]

    rem_cal = max(0.0, cal_target - consumed_calories)
    rem_prot = max(0.0, prot_target - consumed_protein)
    rem_carb = max(0.0, carb_target - consumed_carbs)
    rem_fat = max(0.0, fat_target - consumed_fat)

    over_budget = consumed_calories > cal_target

    # Calculate percentage progress for UI progress rings/bars
    pct_cal = min(100.0, (consumed_calories / cal_target * 100.0)) if cal_target > 0 else 0
    pct_prot = min(100.0, (consumed_protein / prot_target * 100.0)) if prot_target > 0 else 0
    pct_carb = min(100.0, (consumed_carbs / carb_target * 100.0)) if carb_target > 0 else 0
    pct_fat = min(100.0, (consumed_fat / fat_target * 100.0)) if fat_target > 0 else 0

    return {
        "targets": targets,
        "consumed_calories": round(consumed_calories, 1),
        "consumed_protein": round(consumed_protein, 1),
        "consumed_carbohydrates": round(consumed_carbs, 1),
        "consumed_fat": round(consumed_fat, 1),
        "consumed_fiber": round(consumed_fiber, 1),
        "consumed_water": round(consumed_water),
        "remaining_calories": round(rem_cal, 1),
        "remaining_protein": round(rem_prot, 1),
        "remaining_carbohydrates": round(rem_carb, 1),
        "remaining_fat": round(rem_fat, 1),
        "over_budget": over_budget,
        "pct_calories": round(pct_cal, 1),
        "pct_protein": round(pct_prot, 1),
        "pct_carbohydrates": round(pct_carb, 1),
        "pct_fat": round(pct_fat, 1),
    }