from django.contrib import admin
from .models import (
    UserProfile,
    FoodCategory,
    Food,
    DietaryTag,
    Allergen,
    MealLog,
    WaterLog,
    WeightLog,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "gender",
        "height",
        "activity_level",
        "goal",
        "daily_calorie_target",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "gender",
        "activity_level",
        "goal",
    )


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


@admin.register(DietaryTag)
class DietaryTagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "calories",
        "protein",
        "carbohydrates",
        "fat",
        "fiber",
        "serving_size",
        "serving_unit",
    )

    search_fields = (
        "name",
    )

    list_filter = (
        "category",
        "dietary_tags",
        "allergens",
    )

    ordering = (
        "name",
    )


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "food",
        "meal_type",
        "quantity",
        "consumed_at",
    )

    search_fields = (
        "user__username",
        "food__name",
    )

    list_filter = (
        "meal_type",
        "consumed_at",
    )

    ordering = (
        "-consumed_at",
    )


@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount_ml",
        "consumed_at",
    )

    search_fields = (
        "user__username",
    )

    list_filter = (
        "consumed_at",
    )

    ordering = (
        "-consumed_at",
    )


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "weight",
        "recorded_at",
        "notes",
    )

    search_fields = (
        "user__username",
    )

    list_filter = (
        "recorded_at",
    )

    ordering = (
        "-recorded_at",
    )
