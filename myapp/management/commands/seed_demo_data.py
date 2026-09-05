import csv
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from myapp.models import (
    FoodCategory,
    DietaryTag,
    Allergen,
    Food,
    FoodVariant,
)

CATEGORY_MAP = {
    "nepali_staple": "Nepali Meals",
    "nepali_bread": "Nepali Breads & Rotis",
    "nepali_snack": "Nepali Snacks",
    "nepali_curry": "Nepali Curries & Meats",
    "nepali_meat": "Nepali Curries & Meats",
    "nepali_sweet": "Nepali Sweets & Desserts",
    "beverage": "Beverages",
    "international": "International Meals",
}


class Command(BaseCommand):
    help = "Seed NutriAI with NepaliNutriDB (129+ verified Nepali foods, tags, allergens, and variations)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting NepaliNutriDB dataset import...")

        # =========================================
        # 1. ALLERGENS
        # =========================================
        allergens_list = [
            "Milk",
            "Eggs",
            "Peanuts",
            "Tree Nuts",
            "Soy",
            "Gluten",
            "Wheat",
            "Fish",
            "Shellfish",
        ]
        allergen_objs = {}
        for name in allergens_list:
            obj, _ = Allergen.objects.get_or_create(name=name)
            allergen_objs[name] = obj

        # =========================================
        # 2. DIETARY TAGS
        # =========================================
        tags_list = [
            "Vegetarian",
            "Vegan",
            "Gluten Free",
            "Dairy Free",
            "High Protein",
            "Low Carb",
        ]
        tag_objs = {}
        for name in tags_list:
            obj, _ = DietaryTag.objects.get_or_create(name=name)
            tag_objs[name] = obj

        # =========================================
        # 3. FOOD CATEGORIES
        # =========================================
        category_names = [
            "Nepali Meals",
            "Nepali Breads & Rotis",
            "Nepali Snacks",
            "Nepali Curries & Meats",
            "Nepali Sweets & Desserts",
            "Beverages",
            "International Meals",
        ]
        cat_objs = {}
        for name in category_names:
            obj, _ = FoodCategory.objects.get_or_create(name=name)
            cat_objs[name] = obj

        # =========================================
        # 4. LOAD NEPALI FOOD DATASET (CSV)
        # =========================================
        csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "nepali_food_data.csv"
        if not csv_path.exists():
            csv_path = Path("myapp/data/nepali_food_data.csv")

        foods_created = 0
        if csv_path.exists():
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    food_name = row.get("name", "").strip()
                    nepali_name = row.get("name_nepali", "").strip()
                    raw_cat = row.get("category", "").strip().lower()
                    cat_name = CATEGORY_MAP.get(raw_cat, "Nepali Meals")
                    cat_obj = cat_objs.get(cat_name, cat_objs["Nepali Meals"])

                    cal = float(row.get("calories") or 0)
                    prot = float(row.get("protein") or 0)
                    carb = float(row.get("carbohydrates") or 0)
                    fat = float(row.get("fat") or 0)
                    fiber = float(row.get("fiber") or 0)
                    sugar = float(row.get("sugar") or 0)
                    sodium = float(row.get("sodium") or 0)
                    serving_size = float(row.get("serving_size_g") or 100)
                    is_nepali = row.get("is_nepali", "True").lower() == "true"
                    data_source = row.get("data_source", "NepaliNutriDB").strip()

                    food_obj, created = Food.objects.update_or_create(
                        name=food_name,
                        defaults={
                            "name_nepali": nepali_name,
                            "category": cat_obj,
                            "calories": cal,
                            "protein": prot,
                            "carbohydrates": carb,
                            "fat": fat,
                            "fiber": fiber,
                            "sugar": sugar,
                            "sodium": sodium,
                            "serving_size": serving_size,
                            "serving_unit": "g" if serving_size > 10 else "serving",
                            "is_nepali": is_nepali,
                            "data_source": data_source,
                        }
                    )
                    if created:
                        foods_created += 1

                    # Dietary tags associations
                    is_veg = row.get("is_vegetarian", "False").lower() == "true"
                    is_vegan = row.get("is_vegan", "False").lower() == "true"
                    is_gf = row.get("is_gluten_free", "False").lower() == "true"

                    if is_veg:
                        food_obj.dietary_tags.add(tag_objs["Vegetarian"])
                    if is_vegan:
                        food_obj.dietary_tags.add(tag_objs["Vegan"])
                    if is_gf:
                        food_obj.dietary_tags.add(tag_objs["Gluten Free"])
                    if prot >= 15:
                        food_obj.dietary_tags.add(tag_objs["High Protein"])

                    # Allergen associations
                    has_nuts = row.get("contains_nuts", "False").lower() == "true"
                    has_dairy = row.get("contains_dairy", "False").lower() == "true"
                    has_gluten = row.get("contains_gluten", "False").lower() == "true"
                    has_egg = row.get("contains_egg", "False").lower() == "true"

                    if has_nuts:
                        food_obj.allergens.add(allergen_objs["Peanuts"], allergen_objs["Tree Nuts"])
                    if has_dairy:
                        food_obj.allergens.add(allergen_objs["Milk"])
                    if has_gluten:
                        food_obj.allergens.add(allergen_objs["Gluten"], allergen_objs["Wheat"])
                    if has_egg:
                        food_obj.allergens.add(allergen_objs["Eggs"])

            self.stdout.write(f"Imported/Updated {foods_created} foods from NepaliNutriDB CSV.")
        else:
            self.stdout.write(self.style.WARNING(f"CSV file not found at {csv_path}"))

        # =========================================
        # 5. POPULATE COMMON FOOD VARIANTS
        # =========================================
        dal_bhat = Food.objects.filter(name__icontains="Dal Bhat").first()
        if dal_bhat:
            FoodVariant.objects.get_or_create(
                food=dal_bhat,
                name="Vegetarian Tarkari",
                defaults={
                    "calories": 480,
                    "protein": 16,
                    "carbohydrates": 82,
                    "fat": 10,
                    "fiber": 7,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )
            FoodVariant.objects.get_or_create(
                food=dal_bhat,
                name="With Chicken Curry",
                defaults={
                    "calories": 580,
                    "protein": 34,
                    "carbohydrates": 80,
                    "fat": 16,
                    "fiber": 6,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )
            FoodVariant.objects.get_or_create(
                food=dal_bhat,
                name="With Mutton Curry",
                defaults={
                    "calories": 660,
                    "protein": 32,
                    "carbohydrates": 78,
                    "fat": 26,
                    "fiber": 6,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )

        momo = Food.objects.filter(name__icontains="Momo").first()
        if momo:
            FoodVariant.objects.get_or_create(
                food=momo,
                name="Steamed Veg Momo (10 pcs)",
                defaults={
                    "calories": 240,
                    "protein": 8,
                    "carbohydrates": 38,
                    "fat": 6,
                    "fiber": 4,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )
            FoodVariant.objects.get_or_create(
                food=momo,
                name="Steamed Chicken Momo (10 pcs)",
                defaults={
                    "calories": 320,
                    "protein": 22,
                    "carbohydrates": 36,
                    "fat": 10,
                    "fiber": 2,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )
            FoodVariant.objects.get_or_create(
                food=momo,
                name="Steamed Buff Momo (10 pcs)",
                defaults={
                    "calories": 340,
                    "protein": 24,
                    "carbohydrates": 36,
                    "fat": 12,
                    "fiber": 2,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )
            FoodVariant.objects.get_or_create(
                food=momo,
                name="Fried Buff Momo (10 pcs)",
                defaults={
                    "calories": 440,
                    "protein": 24,
                    "carbohydrates": 38,
                    "fat": 22,
                    "fiber": 2,
                    "serving_size": 1,
                    "serving_unit": "plate",
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded database! Total foods available: {Food.objects.count()}"
            )
        )
