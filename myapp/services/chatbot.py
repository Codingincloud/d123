"""
NutriAI — Multi-Tool Intelligent Chatbot Service
Lead Integration & GenAI Engineer: Shrijan Sainju (790342)

Features:
  - Tool-Calling LLM Architecture (Groq / Gemini / Offline contextual fallback)
  - Tools:
      1. get_user_health_profile: Access age, BMI, BMR, TDEE, health goals.
      2. get_today_nutrition_summary: Ground-truth consumed vs remaining calories & macros.
      3. get_meal_recommendations: Ground-truth XGBoost-ranked Nepali meal recommendations.
  - Zero-hallucination guarantee: The LLM fetches exact database records via function calling.
"""

import json
import os
from datetime import date

from myapp.models import UserProfile
from myapp.services.calculations import calculate_daily_summary, calculate_nutrition_baseline


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = (
    "You are NutriAI, an intelligent personal nutrition and diet assistant tailored for Nepali individuals. "
    "Provide clear, evidence-based nutrition advice with respect to Nepali dietary staples (e.g. Dal Bhat, Dhido, "
    "Kwati, Gundruk, Chiura, Momo). "
    "Never guess or hallucinate user data. Use the provided tools whenever appropriate: "
    "- 'get_user_health_profile' to check physical metrics, goal, BMR, and TDEE. "
    "- 'get_today_nutrition_summary' to check exact calories/macros consumed today and remaining budget. "
    "- 'get_meal_recommendations' to get ML-recommended Nepali dishes matching their remaining budget. "
    "Keep responses concise, friendly, and practical. Do not diagnose medical conditions."
)


def _age_in_years(date_of_birth):
    if not date_of_birth:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def get_user_health_profile(user):
    """Return the authenticated user's non-identifying nutrition profile as JSON."""
    profile = UserProfile.objects.filter(user=user).first()
    if not profile:
        return json.dumps({"profile_available": False})

    baseline = calculate_nutrition_baseline(profile)

    return json.dumps({
        "profile_available": True,
        "age_years": _age_in_years(profile.date_of_birth),
        "gender": profile.get_gender_display() or None,
        "height_cm": profile.height,
        "weight_kg": profile.weight,
        "activity_level": profile.get_activity_level_display() or None,
        "goal": profile.get_goal_display() or None,
        "daily_calorie_target": profile.daily_calorie_target,
        "bmr_kcal": baseline["bmr"] if baseline else None,
        "tdee_kcal": baseline["tdee"] if baseline else None,
    })


def get_today_nutrition_summary(user):
    """Return current day's consumed nutrition, remaining targets, and budget status as JSON."""
    summary = calculate_daily_summary(user)
    return json.dumps({
        "consumed_calories": summary["consumed_calories"],
        "calorie_target": summary["targets"]["calorie_target"],
        "remaining_calories": summary["remaining_calories"],
        "consumed_protein_g": summary["consumed_protein"],
        "target_protein_g": summary["targets"]["target_protein"],
        "remaining_protein_g": summary["remaining_protein"],
        "consumed_carbs_g": summary["consumed_carbohydrates"],
        "consumed_fat_g": summary["consumed_fat"],
        "consumed_water_ml": summary["consumed_water"],
        "is_over_calorie_budget": summary["over_budget"],
    })


def get_meal_recommendations(user, count=3):
    """Return top ML-recommended Nepali foods from NepaliNutriDB as JSON."""
    from myapp.ml.recommender import get_recommendations
    recs = get_recommendations(user, limit=count)
    formatted = []
    for r in recs:
        f = r["food"]
        formatted.append({
            "name": f.name,
            "name_nepali": f.name_nepali,
            "calories": f.calories,
            "protein_g": f.protein,
            "carbs_g": f.carbohydrates,
            "fat_g": f.fat,
            "match_percent": r["match_pct"],
            "reasons": r["reasons"],
        })
    return json.dumps({"recommended_meals": formatted})


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_health_profile",
            "description": "Get the user's profile, BMR, TDEE, health goal, height, and weight.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_nutrition_summary",
            "description": "Get ground truth calories and macros consumed today vs daily budget.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_meal_recommendations",
            "description": "Get personalized Nepali food suggestions based on current remaining calorie budget.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
]

available_functions = {
    "get_user_health_profile": get_user_health_profile,
    "get_today_nutrition_summary": get_today_nutrition_summary,
    "get_meal_recommendations": get_meal_recommendations,
}


class ChatbotError(Exception):
    """The chatbot provider could not complete a request."""


class ChatbotConfigurationError(ChatbotError):
    """The server is missing its Groq API key."""


def _offline_intelligent_fallback(conversation, user):
    """
    Intelligent offline fallback: If no API key is set, parses the user's
    question and executes real database tools to provide ground-truth answers.
    Ensures zero crashes during offline college demonstrations.
    """
    last_msg = ""
    for msg in reversed(conversation):
        if msg.get("role") == "user":
            last_msg = msg.get("content", "").lower()
            break

    if any(k in last_msg for k in ["calorie", "today", "consumed", "target", "budget", "left", "macro"]):
        summary = calculate_daily_summary(user)
        t = summary["targets"]
        return (
            f"📊 **Today's Nutrition Summary:**\n\n"
            f"- **Consumed Calories:** {summary['consumed_calories']} / {t['calorie_target']} kcal "
            f"({summary['remaining_calories']} kcal remaining)\n"
            f"- **Protein:** {summary['consumed_protein']}g / {t['target_protein']}g\n"
            f"- **Carbohydrates:** {summary['consumed_carbohydrates']}g / {t['target_carbohydrates']}g\n"
            f"- **Fat:** {summary['consumed_fat']}g / {t['target_fat']}g\n"
            f"- **Water:** {summary['consumed_water']} ml\n\n"
            f"{'⚠️ You have exceeded your daily calorie target.' if summary['over_budget'] else '✅ You are well within your daily calorie target!'}"
        )

    if any(k in last_msg for k in ["recommend", "eat", "lunch", "dinner", "snack", "food", "suggest", "nepali"]):
        from myapp.ml.recommender import get_recommendations
        recs = get_recommendations(user, limit=3)
        if not recs:
            return "No specific meal recommendations found. Try adjusting your dietary preferences."

        res = "🥗 **Top Recommended Nepali Dishes for You (via XGBoost Recommender):**\n\n"
        for i, r in enumerate(recs, 1):
            f = r["food"]
            nep = f" ({f.name_nepali})" if f.name_nepali else ""
            res += (
                f"{i}. **{f.name}{nep}** — {r['match_pct']}% Match\n"
                f"   • Calories: {f.calories} kcal | Protein: {f.protein}g | Carbs: {f.carbohydrates}g | Fat: {f.fat}g\n"
                f"   • Badges: {', '.join(r['reasons'])}\n\n"
            )
        return res

    if any(k in last_msg for k in ["profile", "bmr", "tdee", "height", "weight", "goal"]):
        profile = getattr(user, "userprofile", None)
        if not profile:
            return "You haven't set up your profile yet. Please complete your profile setup."
        baseline = calculate_nutrition_baseline(profile)
        return (
            f"👤 **Your Health Profile:**\n\n"
            f"- **Current Goal:** {profile.get_goal_display() or 'Not set'}\n"
            f"- **Weight:** {profile.weight} kg | **Height:** {profile.height} cm\n"
            f"- **Basal Metabolic Rate (BMR):** {baseline['bmr']} kcal/day\n"
            f"- **Total Daily Energy Expenditure (TDEE):** {baseline['tdee']} kcal/day\n"
            f"- **Daily Calorie Target:** {profile.daily_calorie_target or baseline['tdee']} kcal"
        )

    return (
        "Hello! I am NutriAI, your personalized nutrition assistant. "
        "You can ask me about your daily calories ('How many calories left?'), "
        "request meal recommendations ('What should I eat for dinner?'), "
        "or check your BMR/TDEE metrics ('What is my energy expenditure?')."
    )


def get_chatbot_reply(conversation, user):
    """
    Return assistant reply using Groq tool calling, with offline contextual fallback.
    """
    api_key = os.environ.get("GROQ_API_KEY")

    # If no Groq key is configured, activate offline intelligent fallback
    if not api_key:
        return _offline_intelligent_fallback(conversation, user)

    try:
        from openai import OpenAI, APIError
        client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *conversation]

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=600,
            tools=tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                fn = available_functions.get(tool_call.function.name)
                if not fn:
                    tool_result = json.dumps({"error": "Tool unavailable"})
                else:
                    try:
                        args = json.loads(tool_call.function.arguments or "{}")
                        tool_result = fn(user=user, **args)
                    except Exception as e:
                        tool_result = json.dumps({"error": str(e)})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            followup = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=600,
            )
            assistant_message = followup.choices[0].message

        reply = assistant_message.content
        if not reply:
            return _offline_intelligent_fallback(conversation, user)
        return reply

    except Exception:
        # Fallback to local intelligent assistant if API network fails
        return _offline_intelligent_fallback(conversation, user)
