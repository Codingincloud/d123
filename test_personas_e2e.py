"""
NutriAI — Multi-Persona End-to-End Simulation & Verification
============================================================
Authors & Roles:
  - Prashant Ghimire (790328) — Backend Architecture & Session Routing
  - Romina Koju (790332) — ML Recommendation & Hard Safety Filtering
  - Dristi Shrestha (790312) — UI Views, Dashboard & Profile Integration
  - Shrijan Sainju (790338) — GenAI Assistant & Multi-Persona Dialogues

This script simulates 4 real-world user personas through the full web stack:
  1. Aayush Sharma — Sedentary Weight Loss seeker (Deficit targets, calorie tracking)
  2. Pooja Karki — Vegetarian with Dairy/Lactose allergy (Hard safety exclusions)
  3. Bikram Thapa — Diabetic with Gluten allergy (Celiac safety, low-GI foods)
  4. Sneha Adhikari — Very Active student aiming for muscle gain (Surplus targets, profile edit)
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nutriai.settings")
django.setup()

from datetime import date
from django.test import Client
from django.contrib.auth.models import User
from myapp.models import (
    UserProfile,
    Food,
    Allergen,
    DietaryTag,
    MealLog,
    WaterLog,
    WeightLog,
    RecommendationHistory,
)
from myapp.ml.recommender import get_recommendations
from myapp.services.calculations import (
    calculate_nutrition_baseline,
    calculate_daily_targets,
    calculate_daily_summary,
)
from myapp.services.chatbot import get_chatbot_reply

def run_tests():
    print("=" * 70)
    print("       NUTRIAI MULTI-PERSONA END-TO-END VERIFICATION SUITE       ")
    print("=" * 70)

    client = Client()
    passed = 0
    total = 0

    def check(condition, desc):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {desc}")
        else:
            print(f"  [FAIL] {desc}")
            raise AssertionError(f"Check failed: {desc}")

    # =========================================================================
    # TEST 0: AUTHENTICATION & SECURITY GUARDS
    # =========================================================================
    print("\n[Phase 0] Testing Authentication & Route Protection")
    r = client.get("/dashboard/")
    check(r.status_code == 302 and "/login/" in r.url, "Unauthenticated access to /dashboard/ redirects to /login/")

    r = client.get("/chatbot/")
    check(r.status_code == 302 and "/login/" in r.url, "Unauthenticated access to /chatbot/ redirects to /login/")

    r = client.get("/profile/")
    check(r.status_code == 302 and "/login/" in r.url, "Unauthenticated access to /profile/ redirects to /login/")

    # Password mismatch check
    r = client.post("/register/", {
        "username": "test_mismatch",
        "email": "test@example.com",
        "password1": "pass1",
        "password2": "pass2",
    })
    check(not User.objects.filter(username="test_mismatch").exists(), "Password mismatch in registration rejected")

    # =========================================================================
    # PERSONA 1: Aayush Sharma (Weight Loss & Calorie Deficit)
    # =========================================================================
    print("\n" + "-" * 70)
    print("[Persona 1] Aayush Sharma: Sedentary Weight Loss (Deficit -500 kcal)")
    print("-" * 70)

    User.objects.filter(username="aayush_fit").delete()
    r = client.post("/register/", {
        "username": "aayush_fit",
        "email": "aayush@example.com",
        "password1": "password123",
        "password2": "password123",
    })
    check(User.objects.filter(username="aayush_fit").exists(), "Aayush registered successfully")

    client.post("/login/", {"username": "aayush_fit", "password": "password123"})
    user1 = User.objects.get(username="aayush_fit")

    # Unconfigured profile setup redirect
    r = client.get("/dashboard/")
    check(r.status_code == 302 and "/profile/setup/" in r.url, "New user without profile redirects to /profile/setup/")

    # Setup profile: 26yo Male, 82kg, 172cm, Sedentary, Goal: lose
    r = client.post("/profile/setup/", {
        "date_of_birth": "1998-05-15",
        "gender": "male",
        "height": 172,
        "weight": 82,
        "activity_level": "sedentary",
        "goal": "lose",
        "allergies": [],
        "dietary_tags": [],
    })
    check(UserProfile.objects.filter(user=user1).exists(), "Aayush profile created")

    p1 = user1.userprofile
    baseline1 = calculate_nutrition_baseline(p1)
    targets1 = calculate_daily_targets(p1)
    print(f"    -> Age: {baseline1['age']}, BMR: {baseline1['bmr']} kcal, TDEE: {baseline1['tdee']} kcal, Target: {targets1['calorie_target']} kcal")
    expected_bmr = round(10 * 82 + 6.25 * 172 - 5 * baseline1['age'] + 5)
    expected_tdee = round(expected_bmr * 1.2)
    expected_target = expected_tdee - 500
    check(baseline1["bmr"] == expected_bmr, f"BMR computed accurately (expected {expected_bmr}, got {baseline1['bmr']})")
    check(baseline1["tdee"] == expected_tdee, f"TDEE computed accurately (expected {expected_tdee}, got {baseline1['tdee']})")
    check(targets1["calorie_target"] == expected_target, f"Calorie deficit target computed (expected {expected_target}, got {targets1['calorie_target']})")

    # Load dashboard
    r = client.get("/dashboard/")
    check(r.status_code == 200, "Dashboard loads with status 200")
    check(str(expected_target) in r.content.decode(), f"Dashboard displays goal-adjusted target {expected_target} kcal")

    # Log water
    r = client.post("/dashboard/", {"water_submit": "1", "amount_ml": 500})
    check(WaterLog.objects.filter(user=user1, amount_ml=500).exists(), "500ml water logged via dashboard")

    # Log weight
    r = client.post("/dashboard/", {"weight_submit": "1", "weight": 81.6, "notes": "Morning weigh-in"})
    check(WeightLog.objects.filter(user=user1, weight=81.6).exists(), "Weight record logged via dashboard")

    # Chatbot test for weight loss
    reply = get_chatbot_reply([{"role": "user", "content": "How should I structure my meals to lose weight in Nepal?"}], user1)
    check("Calorie Deficit" in reply or "Dal Bhat" in reply or "deficit" in reply.lower(), "Chatbot returns tailored weight-loss guidance")

    # =========================================================================
    # PERSONA 2: Pooja Karki (Strict Vegetarian + Dairy / Lactose Allergy)
    # =========================================================================
    print("\n" + "-" * 70)
    print("[Persona 2] Pooja Karki: Vegetarian + Dairy/Lactose Allergy (Hard Exclusion)")
    print("-" * 70)

    User.objects.filter(username="pooja_veg").delete()
    client.post("/register/", {
        "username": "pooja_veg",
        "email": "pooja@example.com",
        "password1": "password123",
        "password2": "password123",
    })
    client.post("/login/", {"username": "pooja_veg", "password": "password123"})
    user2 = User.objects.get(username="pooja_veg")

    # Tag & Allergen lookup
    veg_tag = DietaryTag.objects.get(name="Vegetarian")
    milk_alg = Allergen.objects.get(name="Milk")

    client.post("/profile/setup/", {
        "date_of_birth": "2001-09-20",
        "gender": "female",
        "height": 160,
        "weight": 54,
        "activity_level": "moderate",
        "goal": "maintain",
        "allergies": [milk_alg.id],
        "dietary_tags": [veg_tag.id],
    })
    p2 = user2.userprofile

    # Test ML recommendations safety filtering
    recs2 = get_recommendations(user2, limit=6)
    check(len(recs2) > 0, f"Generated {len(recs2)} recommendations for Pooja")

    dairy_found = False
    meat_found = False
    rec_names = []
    for r_item in recs2:
        f = r_item["food"]
        rec_names.append(f.name)
        # Check allergens
        if f.allergens.filter(name__iexact="Milk").exists() or "paneer" in f.name.lower() or "dahi" in f.name.lower() or "milk" in f.name.lower():
            dairy_found = True
        # Check meat
        if not f.dietary_tags.filter(name__iexact="Vegetarian").exists():
            meat_found = True

    print(f"    -> Recommended foods: {', '.join(rec_names)}")
    check(not dairy_found, "ZERO dairy foods recommended (Strict Safety Filter passed)")
    check(not meat_found, "ZERO non-vegetarian foods recommended (Vegetarian filter passed)")

    # 1-click log recommended food
    top_rec = recs2[0]["food"]
    client.post("/dashboard/", {
        "log_recommendation": "1",
        "recommended_food_id": top_rec.id,
        "meal_type": "lunch",
    })
    check(MealLog.objects.filter(user=user2, food=top_rec).exists(), f"Successfully 1-click logged {top_rec.name}")
    check(RecommendationHistory.objects.filter(user=user2, food=top_rec, is_eaten=True).exists(), "Recommendation marked is_eaten=True for behavioral feedback")

    # Chatbot test for high-protein vegetarian
    reply2 = get_chatbot_reply([{"role": "user", "content": "What are high protein vegetarian Nepali foods?"}], user2)
    check("Bhatmas" in reply2 or "Kwati" in reply2 or "protein" in reply2.lower(), "Chatbot returns plant-based protein guidance")

    # =========================================================================
    # PERSONA 3: Bikram Thapa (Diabetic & Gluten-Free / Celiac)
    # =========================================================================
    print("\n" + "-" * 70)
    print("[Persona 3] Bikram Thapa: Diabetic & Gluten-Free (Gluten Allergy Excluded)")
    print("-" * 70)

    User.objects.filter(username="bikram_diabetic").delete()
    client.post("/register/", {
        "username": "bikram_diabetic",
        "email": "bikram@example.com",
        "password1": "password123",
        "password2": "password123",
    })
    client.post("/login/", {"username": "bikram_diabetic", "password": "password123"})
    user3 = User.objects.get(username="bikram_diabetic")

    gf_tag = DietaryTag.objects.get(name="Gluten Free")
    gluten_alg = Allergen.objects.get(name="Gluten")
    wheat_alg = Allergen.objects.get(name="Wheat")

    client.post("/profile/setup/", {
        "date_of_birth": "1972-03-10",
        "gender": "male",
        "height": 168,
        "weight": 74,
        "activity_level": "light",
        "goal": "maintain",
        "allergies": [gluten_alg.id, wheat_alg.id],
        "dietary_tags": [gf_tag.id],
        "custom_dietary_tags": "Diabetic-friendly, low-GI",
    })

    recs3 = get_recommendations(user3, limit=6)
    check(len(recs3) > 0, f"Generated {len(recs3)} recommendations for Bikram")

    gluten_found = False
    rec3_names = []
    for r_item in recs3:
        f = r_item["food"]
        rec3_names.append(f.name)
        if f.allergens.filter(name__in=["Gluten", "Wheat"]).exists():
            gluten_found = True

    print(f"    -> Recommended foods: {', '.join(rec3_names)}")
    check(not gluten_found, "ZERO gluten/wheat foods recommended (Gluten-Free filter passed)")

    # Chatbot test for diabetes & dhido
    reply3 = get_chatbot_reply([{"role": "user", "content": "I have diabetes. Is Kodo ko Dhido good for blood sugar?"}], user3)
    check("Dhido" in reply3 or "glycemic" in reply3.lower() or "sugar" in reply3.lower(), "Chatbot gives specialized low-GI diabetic advice")

    # =========================================================================
    # PERSONA 4: Sneha Adhikari (College Student / Muscle Gain & Surplus)
    # =========================================================================
    print("\n" + "-" * 70)
    print("[Persona 4] Sneha Adhikari: Very Active Muscle Gain (+500 kcal surplus)")
    print("-" * 70)

    User.objects.filter(username="sneha_student").delete()
    client.post("/register/", {
        "username": "sneha_student",
        "email": "sneha@example.com",
        "password1": "password123",
        "password2": "password123",
    })
    client.post("/login/", {"username": "sneha_student", "password": "password123"})
    user4 = User.objects.get(username="sneha_student")

    client.post("/profile/setup/", {
        "date_of_birth": "2003-11-12",
        "gender": "female",
        "height": 158,
        "weight": 48,
        "activity_level": "very",
        "goal": "gain",
        "allergies": [],
        "dietary_tags": [],
    })
    p4 = user4.userprofile
    baseline4 = calculate_nutrition_baseline(p4)
    targets4 = calculate_daily_targets(p4)
    print(f"    -> BMR: {baseline4['bmr']} kcal, TDEE: {baseline4['tdee']} kcal, Surplus Target: {targets4['calorie_target']} kcal")
    check(targets4["calorie_target"] == baseline4["tdee"] + 500, "Surplus calorie target (+500 kcal) verified")
    check(targets4["target_protein"] > 140, f"High protein split for muscle gain verified ({targets4['target_protein']}g)")

    # Test profile edit view: change weight to 49kg
    r = client.post("/profile/edit/", {
        "first_name": "Sneha",
        "last_name": "Adhikari",
        "email": "sneha@example.com",
        "gender": "female",
        "height": 158,
        "weight": 49,
        "activity_level": "very",
        "goal": "gain",
    })
    check(r.status_code == 302, "Profile edit succeeds and redirects to dashboard")
    p4.refresh_from_db()
    check(p4.weight == 49.0, "Updated weight reflected in database")

    # Profile display check
    r = client.get("/profile/")
    check(r.status_code == 200, "Profile page loads with status 200")
    check("Sneha Adhikari" in r.content.decode(), "Profile page displays user first & last name")
    check("BMR (Mifflin-St Jeor)" in r.content.decode(), "Profile page displays scientific BMR")

    # Chatbot test for muscle building
    reply4 = get_chatbot_reply([{"role": "user", "content": "Suggest a high protein Nepali diet plan for muscle gain"}], user4)
    check("Bhatmas" in reply4 or "Choila" in reply4 or "Eggs" in reply4 or "protein" in reply4.lower(), "Chatbot returns muscle building diet recommendations")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print(f"VERIFICATION COMPLETE: {passed}/{total} CHECKS PASSED SUCCESSFULLY (100%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
