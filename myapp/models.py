from django.db import models

# Create your models here.
from django.contrib.auth.models import User
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES,blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    activity_level = models.CharField(max_length=30, blank=True)
    goal = models.CharField(max_length=30, blank=True)
    daily_calorie_target = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DietaryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Food(models.Model):
    name = models.CharField(max_length=150)

    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="foods"
    )

    dietary_tags = models.ManyToManyField(
        DietaryTag,
        blank=True,
        related_name="foods"
    )

    allergens = models.ManyToManyField(
        Allergen,
        blank=True,
        related_name="foods"
    )

    calories = models.FloatField()
    protein = models.FloatField(default=0)
    carbohydrates = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    fiber = models.FloatField(default=0)

    serving_size = models.FloatField(default=100)
    serving_unit = models.CharField(max_length=30, default="g")

    def __str__(self):
        return self.name
    
class MealLog(models.Model):
    MEAL_TYPES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meal_logs"
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name="meal_logs"
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPES
    )

    quantity = models.FloatField(default=1)

    consumed_at = models.DateTimeField()

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.food.name}"
    
class WaterLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="water_logs"
    )

    amount_ml = models.FloatField()

    consumed_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.amount_ml} ml"
    
class WeightLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="weight_logs"
    )

    weight = models.FloatField()

    recorded_at = models.DateTimeField()

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.weight} kg"