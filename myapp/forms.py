from django import forms
from .models import UserProfile


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
                attrs={"type": "date"}
            ),
            "gender": forms.Select(
                choices=[
                    ("", "Select Gender"),
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Other", "Other"),
                ]
            ),
            "activity_level": forms.Select(
                choices=[
                    ("", "Select Activity Level"),
                    ("Sedentary", "Sedentary"),
                    ("Light", "Lightly Active"),
                    ("Moderate", "Moderately Active"),
                    ("Active", "Very Active"),
                ]
            ),
            "goal": forms.Select(
                choices=[
                    ("", "Select Goal"),
                    ("Lose", "Lose Weight"),
                    ("Maintain", "Maintain Weight"),
                    ("Gain", "Gain Weight"),
                ]
            ),
        }