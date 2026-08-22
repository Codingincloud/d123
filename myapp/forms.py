from django import forms
from django.utils import timezone
from .models import (
    UserProfile,
    FoodCategory,
    DietaryTag,
    Allergen,
    Food,
    MealLog,
    WaterLog,
    WeightLog,
)


# ==========================
# USER PROFILE FORM
# ==========================

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "date_of_birth",
            "gender",
            "height",
            "weight",
            "activity_level",
            "goal",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "gender": forms.Select(
                choices=[
                    ("", "Select Gender"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ],
                attrs={"class": "form-control"}
            ),
            "activity_level": forms.Select(
                choices=[
                    ("", "Select Activity Level"),
                    ("Sedentary", "Sedentary"),
                    ("Light", "Lightly Active"),
                    ("Moderate", "Moderately Active"),
                    ("Active", "Very Active"),
                ],
                attrs={"class": "form-control"}
            ),
            "goal": forms.Select(
                choices=[
                    ("", "Select Goal"),
                    ("Lose", "Lose Weight"),
                    ("Maintain", "Maintain Weight"),
                    ("Gain", "Gain Weight"),
                ],
                attrs={"class": "form-control"}
            ),
            "height": forms.NumberInput(attrs={"placeholder": "Height in cm", "class": "form-control"}),
            "weight": forms.NumberInput(attrs={"placeholder": "Weight in kg", "class": "form-control"}),
        }


# ==========================
# FOOD MANAGEMENT FORMS
# ==========================

class FoodCategoryForm(forms.ModelForm):
    class Meta:
        model = FoodCategory
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Category Name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional description..."}),
        }


class DietaryTagForm(forms.ModelForm):
    class Meta:
        model = DietaryTag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Vegan, Keto, Gluten-Free"}),
        }


class AllergenForm(forms.ModelForm):
    class Meta:
        model = Allergen
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Peanuts, Dairy, Shellfish"}),
        }


class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = [
            "name",
            "category",
            "dietary_tags",
            "allergens",
            "calories",
            "protein",
            "carbohydrates",
            "fat",
            "fiber",
            "serving_size",
            "serving_unit",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Food item name"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "dietary_tags": forms.CheckboxSelectMultiple(),
            "allergens": forms.CheckboxSelectMultiple(),
            "calories": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "protein": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "carbohydrates": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "fat": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "fiber": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "serving_size": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "serving_unit": forms.TextInput(attrs={"class": "form-control", "placeholder": "g, ml, oz, piece"}),
        }


# ==========================
# USER LOGGING FORMS
# ==========================

class MealLogForm(forms.ModelForm):
    class Meta:
        model = MealLog
        fields = ["food", "meal_type", "quantity", "consumed_at", "notes"]
        widgets = {
            "food": forms.Select(attrs={"class": "form-control"}),
            "meal_type": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "0.1"}),
            "consumed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Optional notes..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill current datetime if creating a new log
        if not self.instance.pk:
            self.fields["consumed_at"].initial = timezone.now().strftime("%Y-%m-%dT%H:%M")


class WaterLogForm(forms.ModelForm):
    class Meta:
        model = WaterLog
        fields = ["amount_ml", "consumed_at"]
        widgets = {
            "amount_ml": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount in ml (e.g. 250)"}),
            "consumed_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["consumed_at"].initial = timezone.now().strftime("%Y-%m-%dT%H:%M")


class WeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ["weight", "recorded_at", "notes"]
        widgets = {
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "placeholder": "Weight in kg"}),
            "recorded_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M"
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Optional notes..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["recorded_at"].initial = timezone.now().strftime("%Y-%m-%dT%H:%M")