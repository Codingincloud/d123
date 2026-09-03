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
    if not weight or not height or not age:
        return None

    if gender == "male":

        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            + 5
        )

    elif gender == "female":

        bmr = (
            10 * weight
            + 6.25 * height
            - 5 * age
            - 161
        )

    else:
        return None

    return round(bmr)


def calculate_tdee(
    bmr,
    activity_level
):
    if not bmr or not activity_level:
        return None

    activity_multipliers = {

        "sedentary": 1.2,

        "light": 1.375,

        "moderate": 1.55,

        "very": 1.725,
    }

    multiplier = activity_multipliers.get(
        activity_level
    )

    if not multiplier:
        return None

    tdee = bmr * multiplier

    return round(tdee)


def calculate_nutrition_baseline(profile):
    """
    Calculate the user's basic nutrition metrics.

    This function does NOT decide the user's final
    calorie or macro goals. Those will be handled
    later by the AI recommendation engine.
    """

    age = calculate_age(
        profile.date_of_birth
    )

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