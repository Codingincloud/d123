from django.contrib import admin
from .models import (
    UserProfile,
    FoodCategory,
    DietaryTag,
    Allergen,
    Food,
    FoodVariant,
    MealLog,
    WaterLog,
    WeightLog,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'gender',
        'height',
        'weight',   
        'activity_level',
        'goal',
        'daily_calorie_target',
        'display_allergies',
        'display_dietary_tags',
    )
 
    def display_allergies(self, obj):
            return ", ".join(
                allergy.name for allergy in obj.allergies.all()
            )

    display_allergies.short_description = "Allergies"

    def display_dietary_tags(self, obj):
            return ", ".join(
                tag.name for tag in obj.dietary_tags.all()
            )

    display_dietary_tags.short_description = "Dietary Tags"
    search_fields = (
        'user__username',
        'user__email',
    )

    list_filter = (
        'gender',
        'activity_level',
        'goal',
    )


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )

    search_fields = ('name',)


@admin.register(DietaryTag)
class DietaryTagAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'calories',
        'protein',
        'carbohydrates',
        'fat',
        'fiber',
        'serving_size',
        'serving_unit',
    )

    search_fields = ('name',)

    list_filter = ('category', 'dietary_tags', 'allergens')

    filter_horizontal = (
        'dietary_tags',
        'allergens',
    )

@admin.register(FoodVariant)
class FoodVariantAdmin(admin.ModelAdmin):
    list_display = (
        'food',
        'name',
        'calories',
        'protein',
        'carbohydrates',
        'fat',
        'fiber',
        'serving_size',
        'serving_unit',
    )

    search_fields = (
        'food__name',
        'name',
    )

    list_filter = (
        'food',
    )


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "food_name",
        "category",
        "meal_type",
        "quantity",
        "calories",
        "protein",
        "carbohydrates",
        "fat",
        "fiber",
        "consumed_at",
    )

    list_filter = (
        "meal_type",
        "food__category",
    )

    search_fields = (
        "user__username",
        "food_name",
        "food__name",
    )

    def category(self, obj):
        if obj.food and obj.food.category:
            return obj.food.category.name
        return "-"

    def protein(self, obj):
        if obj.food:
            return obj.food.protein
        return 0

    def carbohydrates(self, obj):
        if obj.food:
            return obj.food.carbohydrates
        return 0

    def fat(self, obj):
        if obj.food:
            return obj.food.fat
        return 0

    def fiber(self, obj):
        if obj.food:
            return obj.food.fiber
        return 0

    category.short_description = "Category"
    protein.short_description = "Protein"
    carbohydrates.short_description = "Carbohydrates"
    fat.short_description = "Fat"
    fiber.short_description = "Fiber"


@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'amount_ml',
        'consumed_at',
    )

    search_fields = (
        'user__username',
    )

    list_filter = ('consumed_at',)


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'weight',
        'recorded_at',
    )

    search_fields = (
        'user__username',
    )

    list_filter = ('recorded_at',)