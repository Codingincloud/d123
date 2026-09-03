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

        # -------------------------
        # Allergens
        # -------------------------

        allergens = [
            "Milk",
            "Eggs",
            "Peanuts",
            "Tree Nuts",
            "Soy",
        ]

        for name in allergens:
            Allergen.objects.get_or_create(
                name=name
            )


        # -------------------------
        # Dietary Tags
        # -------------------------

        dietary_tags = [
            "Vegetarian",
            "Vegan",
            "Gluten Free",
            "Dairy Free",
            "High Protein",
        ]

        for name in dietary_tags:
            DietaryTag.objects.get_or_create(
                name=name
            )


        # -------------------------
        # Food Categories
        # -------------------------

        categories = [
            "Nepali Meals",
            "Snacks",
            "Beverages",
        ]

        category_objects = {}

        for name in categories:

            category, created = FoodCategory.objects.get_or_create(
                name=name
            )

            category_objects[name] = category


        # -------------------------
        # Foods
        # -------------------------

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


        # -------------------------
        # Food Variants
        # -------------------------

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


        self.stdout.write(
            self.style.SUCCESS(
                "NutriAI demo data added successfully!"
            )
        )