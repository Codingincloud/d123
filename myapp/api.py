"""
NutriAI — REST API Compatibility Layer
Backend Lead: Prashant Ghimire (790328)

Exposes JSON endpoints for mobile apps, external clients, and React frontends.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from myapp.models import Food, MealLog, UserProfile, RecommendationHistory
from myapp.services.calculations import calculate_daily_summary, calculate_daily_targets, calculate_nutrition_baseline
from myapp.services.chatbot import get_chatbot_reply
from myapp.ml.recommender import get_recommendations


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = request.POST

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    user = authenticate(username=username, password=password)
    if user:
        profile = getattr(user, "userprofile", None)
        return JsonResponse({
            "access": f"mock_token_{user.id}_{int(timezone.now().timestamp())}",
            "refresh": f"refresh_{user.id}",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "goal": profile.goal if profile else "maintain",
            }
        })
    return JsonResponse({"error": "Invalid username or password"}, status=401)


@csrf_exempt
def api_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = request.POST

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password") or data.get("password1", "")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.create(user=user)

    return JsonResponse({
        "message": "User registered successfully",
        "access": f"mock_token_{user.id}",
        "user": {"id": user.id, "username": user.username}
    }, status=201)


def api_foods(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    qs = Food.objects.all()
    if query:
        qs = qs.filter(name__icontains=query)
    if category:
        qs = qs.filter(category__name__icontains=category)

    foods_data = []
    for f in qs[:50]:
        foods_data.append({
            "id": f.id,
            "name": f.name,
            "name_nepali": f.name_nepali,
            "category": f.category.name if f.category else None,
            "calories": f.calories,
            "protein": f.protein,
            "carbohydrates": f.carbohydrates,
            "fat": f.fat,
            "fiber": f.fiber,
            "serving_size": f.serving_size,
            "serving_unit": f.serving_unit,
            "is_nepali": f.is_nepali,
        })

    return JsonResponse({"count": len(foods_data), "results": foods_data})


def api_recommendations(request):
    # Find active user or fallback to prashant
    user = request.user if request.user.is_authenticated else User.objects.filter(username="prashant").first()
    if not user:
        user = User.objects.first()

    if not user:
        return JsonResponse({"error": "No user available"}, status=400)

    recs = get_recommendations(user, limit=6)
    results = []
    for r in recs:
        f = r["food"]
        results.append({
            "food_id": f.id,
            "name": f.name,
            "name_nepali": f.name_nepali,
            "calories": f.calories,
            "protein": f.protein,
            "carbohydrates": f.carbohydrates,
            "fat": f.fat,
            "match_score": r["match_pct"],
            "ml_score": r["ml_score"],
            "budget_score": r["budget_score"],
            "reasons": r["reasons"],
        })

    return JsonResponse({"recommendations": results})


@csrf_exempt
def api_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = request.user if request.user.is_authenticated else User.objects.filter(username="prashant").first()
    if not user:
        user = User.objects.first()

    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        data = request.POST

    message = data.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Message required"}, status=400)

    history = data.get("history", [])
    history.append({"role": "user", "content": message})

    reply = get_chatbot_reply(history, user)
    return JsonResponse({"reply": reply, "message": reply})
