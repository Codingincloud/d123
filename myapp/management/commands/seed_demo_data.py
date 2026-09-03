
from django.core.management.base import BaseCommand
from myapp.models import (
    FoodCategory,
    DietaryTag,
    Allergen,
    Food,
    FoodVariant,
)


class Command(BaseCommand):
    help = "Add demo data for NutriAI"

    def handle(self, *args, **kwargs):

        # =========================================
        # ALLERGENS
        # =========================================

        allergens = [
            "Milk",
            "Eggs",
            "Peanuts",
            "Tree Nuts",
            "Soy",
        ]

        allergen_objects = {}

        for name in allergens:
            allergen, _ = Allergen.objects.get_or_create(name=name)
            allergen_objects[name] = allergen

        # =========================================
        # DIETARY TAGS
        # =========================================

        dietary_tags = [
            "Vegetarian",
            "Vegan",
            "Gluten Free",
            "Dairy Free",
            "High Protein",
        ]

        dietary_tag_objects = {}

        for name in dietary_tags:
            tag, _ = DietaryTag.objects.get_or_create(name=name)
            dietary_tag_objects[name] = tag

        # =========================================
        # FOOD CATEGORIES
        # =========================================

        categories = [
            "Nepali Meals",
            "Snacks",
            "Beverages",
        ]

        category_objects = {}

        for name in categories:
            category, _ = FoodCategory.objects.get_or_create(name=name)
            category_objects[name] = category

        # =========================================
        # FOODS
        # =========================================

        dal_bhat, _ = Food.objects.get_or_create(
            name="Dal Bhat",
            defaults={
                "category": category_objects["Nepali Meals"],
                "calories": 450,
                "protein": 15,
                "carbohydrates": 75,
                "fat": 10,
                "fiber": 8,
                "serving_size": 1,
                "serving_unit": "plate",
            }
        )

        momo, _ = Food.objects.get_or_create(
            name="Momo",
            defaults={
                "category": category_objects["Nepali Meals"],
                "calories": 250,
                "protein": 10,
                "carbohydrates": 30,
                "fat": 10,
                "fiber": 2,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        chowmein, _ = Food.objects.get_or_create(
            name="Chowmein",
            defaults={
                "category": category_objects["Nepali Meals"],
                "calories": 350,
                "protein": 12,
                "carbohydrates": 50,
                "fat": 12,
                "fiber": 4,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        sel_roti, _ = Food.objects.get_or_create(
            name="Sel Roti",
            defaults={
                "category": category_objects["Snacks"],
                "calories": 180,
                "protein": 3,
                "carbohydrates": 25,
                "fat": 8,
                "fiber": 1,
                "serving_size": 1,
                "serving_unit": "piece",
            }
        )

        milk, _ = Food.objects.get_or_create(
            name="Milk",
            defaults={
                "category": category_objects["Beverages"],
                "calories": 120,
                "protein": 6,
                "carbohydrates": 9,
                "fat": 6,
                "fiber": 0,
                "serving_size": 250,
                "serving_unit": "ml",
            }
        )

        # =========================================
        # FOOD VARIATIONS
        # =========================================

        # ---------- DAL BHAT ----------

        FoodVariant.objects.get_or_create(
            food=dal_bhat,
            name="Vegetarian",
            defaults={
                "calories": 450,
                "protein": 15,
                "carbohydrates": 75,
                "fat": 10,
                "fiber": 8,
                "serving_size": 1,
                "serving_unit": "plate",
            }
        )

        FoodVariant.objects.get_or_create(
            food=dal_bhat,
            name="Chicken",
            defaults={
                "calories": 550,
                "protein": 35,
                "carbohydrates": 75,
                "fat": 15,
                "fiber": 8,
                "serving_size": 1,
                "serving_unit": "plate",
            }
        )

        FoodVariant.objects.get_or_create(
            food=dal_bhat,
            name="Mutton",
            defaults={
                "calories": 650,
                "protein": 32,
                "carbohydrates": 75,
                "fat": 27,
                "fiber": 8,
                "serving_size": 1,
                "serving_unit": "plate",
            }
        )

        # ---------- MOMO ----------

        FoodVariant.objects.get_or_create(
            food=momo,
            name="Chicken",
            defaults={
                "calories": 280,
                "protein": 14,
                "carbohydrates": 30,
                "fat": 11,
                "fiber": 2,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        FoodVariant.objects.get_or_create(
            food=momo,
            name="Buff",
            defaults={
                "calories": 300,
                "protein": 16,
                "carbohydrates": 30,
                "fat": 13,
                "fiber": 2,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        FoodVariant.objects.get_or_create(
            food=momo,
            name="Vegetable",
            defaults={
                "calories": 220,
                "protein": 7,
                "carbohydrates": 32,
                "fat": 7,
                "fiber": 4,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        # ---------- CHOWMEIN ----------

        FoodVariant.objects.get_or_create(
            food=chowmein,
            name="Chicken",
            defaults={
                "calories": 400,
                "protein": 18,
                "carbohydrates": 50,
                "fat": 14,
                "fiber": 4,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        FoodVariant.objects.get_or_create(
            food=chowmein,
            name="Buff",
            defaults={
                "calories": 430,
                "protein": 20,
                "carbohydrates": 50,
                "fat": 17,
                "fiber": 4,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        FoodVariant.objects.get_or_create(
            food=chowmein,
            name="Vegetable",
            defaults={
                "calories": 330,
                "protein": 9,
                "carbohydrates": 52,
                "fat": 10,
                "fiber": 5,
                "serving_size": 1,
                "serving_unit": "serving",
            }
        )

        # ---------- SEL ROTI ----------

        FoodVariant.objects.get_or_create(
            food=sel_roti,
            name="Plain",
            defaults={
                "calories": 180,
                "protein": 3,
                "carbohydrates": 25,
                "fat": 8,
                "fiber": 1,
                "serving_size": 1,
                "serving_unit": "piece",
            }
        )

        FoodVariant.objects.get_or_create(
            food=sel_roti,
            name="Sweet",
            defaults={
                "calories": 210,
                "protein": 3,
                "carbohydrates": 32,
                "fat": 8,
                "fiber": 1,
                "serving_size": 1,
                "serving_unit": "piece",
            }
        )

        # ---------- MILK ----------

        FoodVariant.objects.get_or_create(
            food=milk,
            name="Full Cream",
            defaults={
                "calories": 150,
                "protein": 8,
                "carbohydrates": 12,
                "fat": 8,
                "fiber": 0,
                "serving_size": 250,
                "serving_unit": "ml",
            }
        )

        FoodVariant.objects.get_or_create(
            food=milk,
            name="Low Fat",
            defaults={
                "calories": 105,
                "protein": 8,
                "carbohydrates": 12,
                "fat": 3,
                "fiber": 0,
                "serving_size": 250,
                "serving_unit": "ml",
            }
        )

        FoodVariant.objects.get_or_create(
            food=milk,
            name="Skimmed",
            defaults={
                "calories": 85,
                "protein": 8,
                "carbohydrates": 12,
                "fat": 0.5,
                "fiber": 0,
                "serving_size": 250,
                "serving_unit": "ml",
            }
        )

        # =========================================
        # FOOD DIETARY TAGS
        # =========================================

        dal_bhat.dietary_tags.add(
            dietary_tag_objects["Vegetarian"]
        )

        momo.dietary_tags.add(
            dietary_tag_objects["Vegetarian"]
        )

        # =========================================
        # SUCCESS MESSAGE
        # =========================================

        self.stdout.write(
            self.style.SUCCESS(
                "NutriAI demo data with food variations added successfully!"
            )
        )

