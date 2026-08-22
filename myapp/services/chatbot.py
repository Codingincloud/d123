"""Groq-backed chatbot service.

Keep model and tool orchestration here so views stay independent of the AI provider.
"""

import json
import os
from datetime import date

from openai import APIError, OpenAI

from myapp.models import UserProfile


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"
SYSTEM_PROMPT = (
    "You are NutriAI, a helpful nutrition assistant. Give clear, practical general "
    "nutrition guidance. Do not diagnose medical conditions; recommend a qualified "
    "professional for medical concerns. Use the get_user_health_profile tool when "
    "the user's saved profile data would help answer their question."
)


def _age_in_years(date_of_birth):
    """Return the user's age without exposing their exact birth date."""
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

    return json.dumps(
        {
            "profile_available": True,
            "age_years": _age_in_years(profile.date_of_birth),
            "gender": profile.get_gender_display() or None,
            "height_cm": profile.height,
            "profile_weight_kg": profile.weight,
            "activity_level": profile.get_activity_level_display() or None,
            "goal": profile.get_goal_display() or None,
            "daily_calorie_target": profile.daily_calorie_target,
        }
    )


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_health_profile",
            "description": (
                "Get the current authenticated user's saved nutrition profile, including "
                "their height, weight, activity level, goal, calorie target, and age."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
]


# Map the model's function name to the server-side implementation.
available_functions = {
    "get_user_health_profile": get_user_health_profile,
}


class ChatbotError(Exception):
    """The chatbot provider could not complete a request."""


class ChatbotConfigurationError(ChatbotError):
    """The server is missing its Groq API key."""


def get_chatbot_reply(conversation, user):
    """Return one assistant reply for a browser-safe conversation history.

    The authenticated user is passed only to server-side tool functions, never to the model.
    """
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ChatbotConfigurationError

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *conversation]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=500,
            tools=tools,
            tool_choice="auto",
        )
    except APIError as error:
        raise ChatbotError from error

    assistant_message = response.choices[0].message

    if assistant_message.tool_calls:
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            function = available_functions.get(tool_call.function.name)

            if not function:
                tool_result = json.dumps({"error": "Requested tool is unavailable."})
            else:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    tool_result = function(user=user, **arguments)
                except (TypeError, ValueError) as error:
                    tool_result = json.dumps({"error": f"Tool could not run: {error}"})

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.4,
                max_tokens=500,
            )
        except APIError as error:
            raise ChatbotError from error

        assistant_message = response.choices[0].message

    reply = assistant_message.content
    if not reply:
        raise ChatbotError

    return reply
