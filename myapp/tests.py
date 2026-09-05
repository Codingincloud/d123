from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

from myapp.ml.dataset import compute_nutritional_score
from myapp.ml.recommender import get_recommendations
from myapp.models import Allergen, DietaryTag, Food, FoodCategory, MealLog, UserProfile
from myapp.services.calculations import (
    calculate_age,
    calculate_bmr,
    calculate_daily_summary,
    calculate_daily_targets,
    calculate_tdee,
)
from myapp.services.chatbot import (
    get_meal_recommendations,
    get_today_nutrition_summary,
    get_user_health_profile,
    _offline_intelligent_fallback,
)


class NutritionCalculationsTestCase(TestCase):
    """Unit tests for Mifflin-St Jeor BMR, TDEE, and daily target calculations."""

    def test_calculate_bmr_male(self):
        # Male, 70kg, 175cm, 25 years old
        # BMR = (10 * 70) + (6.25 * 175) - (5 * 25) + 5 = 700 + 1093.75 - 125 + 5 = 1673.75 -> 1674
        bmr = calculate_bmr(weight=70, height=175, age=25, gender="male")
        self.assertEqual(bmr, 1674)

    def test_calculate_bmr_female(self):
        # Female, 60kg, 160cm, 24 years old
        # BMR = (10 * 60) + (6.25 * 160) - (5 * 24) - 161 = 600 + 1000 - 120 - 161 = 1319
        bmr = calculate_bmr(weight=60, height=160, age=24, gender="female")
        self.assertEqual(bmr, 1319)

    def test_calculate_tdee(self):
        bmr = 1600
        self.assertEqual(calculate_tdee(bmr, "sedentary"), round(1600 * 1.2))
        self.assertEqual(calculate_tdee(bmr, "moderate"), round(1600 * 1.55))

    def test_calculate_daily_targets_weight_loss(self):
        user = User.objects.create_user(username="test_loss")
        profile = UserProfile.objects.create(
            user=user,
            gender="male",
            weight=80,
            height=180,
            activity_level="moderate",
            goal="lose",
            date_of_birth=date(2000, 1, 1),
        )
        targets = calculate_daily_targets(profile)
        # Should apply -500 kcal deficit
        baseline_tdee = calculate_tdee(calculate_bmr(80, 180, 26, "male"), "moderate")
        self.assertEqual(targets["calorie_target"], baseline_tdee - 500)
        self.assertGreater(targets["target_protein"], 0)
        self.assertGreater(targets["target_carbohydrates"], 0)
        self.assertGreater(targets["target_fat"], 0)


class NepaliNutriDBTestCase(TestCase):
    """Unit tests for NepaliNutriDB food model and features."""

    def setUp(self):
        self.cat = FoodCategory.objects.create(name="Nepali Meals")
        self.veg_tag = DietaryTag.objects.create(name="Vegetarian")
        self.peanut_allergy = Allergen.objects.create(name="Peanuts")

        self.dal_bhat = Food.objects.create(
            name="Dal Bhat",
            name_nepali="दाल भात",
            category=self.cat,
            calories=450,
            protein=16,
            carbohydrates=75,
            fat=8,
            fiber=7,
            serving_size=300,
            serving_unit="g",
            is_nepali=True,
        )
        self.dal_bhat.dietary_tags.add(self.veg_tag)

    def test_food_str_representation(self):
        self.assertEqual(str(self.dal_bhat), "Dal Bhat (दाल भात)")

    def test_nutritional_quality_scoring(self):
        score = compute_nutritional_score(
            calories=450,
            protein=20,
            carbohydrates=60,
            fat=8,
            fiber=8,
            sugar=2,
            sodium=150,
        )
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 1.0)


class HybridRecommendationTestCase(TestCase):
    """Unit tests for ML recommendation engine and safety filters."""

    def setUp(self):
        self.user = User.objects.create_user(username="rec_user", password="password123")
        self.peanut_allergy = Allergen.objects.create(name="Peanuts")
        self.veg_tag = DietaryTag.objects.create(name="Vegetarian")

        self.profile = UserProfile.objects.create(
            user=self.user,
            weight=70,
            height=175,
            gender="male",
            activity_level="moderate",
            goal="maintain",
            date_of_birth=date(2001, 3, 10),
        )
        self.profile.allergies.add(self.peanut_allergy)
        self.profile.dietary_tags.add(self.veg_tag)

        # Safe Nepali food
        self.kwati = Food.objects.create(
            name="Kwati",
            name_nepali="क्वाटी",
            calories=180,
            protein=12,
            carbohydrates=28,
            fat=2,
            fiber=9,
            is_nepali=True,
        )
        self.kwati.dietary_tags.add(self.veg_tag)

        # Unsafe food containing peanuts
        self.bad_food = Food.objects.create(
            name="Peanut Sadeko",
            calories=300,
            protein=10,
            carbohydrates=15,
            fat=22,
            fiber=3,
        )
        self.bad_food.allergens.add(self.peanut_allergy)

    def test_allergen_hard_exclusion(self):
        recs = get_recommendations(self.user, limit=10)
        rec_food_names = [r["food"].name for r in recs]
        # Peanut Sadeko must be strictly filtered out by allergen safety filter
        self.assertNotIn("Peanut Sadeko", rec_food_names)
        self.assertIn("Kwati", rec_food_names)


class ChatbotToolCallingTestCase(TestCase):
    """Unit tests for Chatbot tools and offline intelligence fallback."""

    def setUp(self):
        self.user = User.objects.create_user(username="chat_user", password="password123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            weight=65,
            height=170,
            gender="female",
            activity_level="light",
            goal="lose",
            date_of_birth=date(2002, 6, 20),
            daily_calorie_target=1500,
        )

    def test_get_user_health_profile_tool(self):
        result_json = get_user_health_profile(self.user)
        self.assertIn("profile_available", result_json)
        self.assertIn("1500", result_json)

    def test_get_today_nutrition_summary_tool(self):
        result_json = get_today_nutrition_summary(self.user)
        self.assertIn("consumed_calories", result_json)
        self.assertIn("remaining_calories", result_json)

    def test_offline_fallback_response(self):
        convo = [{"role": "user", "content": "How many calories do I have today?"}]
        reply = _offline_intelligent_fallback(convo, self.user)
        self.assertIn("Today's Nutrition Summary", reply)
        self.assertIn("Consumed Calories", reply)
