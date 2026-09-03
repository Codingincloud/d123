from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserEditForm, ProfileEditForm

from .services.calculations import calculate_nutrition_baseline
from .services.chatbot import ChatbotConfigurationError, ChatbotError, get_chatbot_reply

from .models import (
    UserProfile,
    FoodCategory,
    DietaryTag,
    Allergen,
    Food,
    MealLog,
    WaterLog,
    WeightLog,
    FoodVariant
)

from .forms import (
    UserProfileForm,
    FoodCategoryForm,
    DietaryTagForm,
    AllergenForm,
    FoodForm,
    MealLogForm,
    WaterLogForm,
    WeightLogForm,
)


# ==========================
# BASIC PAGES
# ==========================

def index(request):
    return render(request, "index.html")


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


@login_required
def chatbot(request):
    history = request.session.get("chatbot_history", [])

    if request.method == "POST":
        if request.POST.get("action") == "clear":
            request.session["chatbot_history"] = []
            return redirect("chatbot")

        user_message = request.POST.get("message", "").strip()

        if user_message:
            if len(user_message) > 2000:
                messages.error(request, "Please keep messages to 2,000 characters or fewer.")
                return redirect("chatbot")

            history.append({"role": "user", "content": user_message})

            try:
                assistant_reply = get_chatbot_reply(history, request.user)
            except ChatbotConfigurationError:
                messages.error(request, "The chatbot is not configured yet. Add GROQ_API_KEY to your .env file.")
                return redirect("chatbot")
            except ChatbotError:
                messages.error(request, "The chatbot could not respond right now. Please try again.")
                return redirect("chatbot")

            history.append({"role": "assistant", "content": assistant_reply})
            request.session["chatbot_history"] = history[-12:]
            request.session.modified = True

        return redirect("chatbot")

    return render(request, "chatbot.html", {"chat_history": history})


# ==========================
# REGISTER
# ==========================

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(request, "register.html")


# ==========================
# LOGIN
# ==========================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin/staff users
            if user.is_staff or user.is_superuser:
                return redirect("userdash")

            # Regular users
            try:

                UserProfile.objects.get(user=user)

                # Profile exists
                return redirect("userdash")

            except UserProfile.DoesNotExist:

                # Profile doesn't exist
                return redirect("profilesetup")

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

            return redirect("login")

    return render(request, "login.html")


# ==========================
# LOGOUT
# ==========================

def user_logout(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect("index")


# ==========================
# USER DASHBOARD
# ==========================

@login_required
def userdash(request):

    # --------------------------
    # PROFILE CHECK
    # --------------------------

    if not request.user.is_staff and not request.user.is_superuser:

        try:

            profile = UserProfile.objects.get(
                user=request.user
            )

        except UserProfile.DoesNotExist:

            return redirect("profilesetup")
        
        baseline = calculate_nutrition_baseline(profile)

    else:

        profile = None


    # --------------------------
    # CREATE FORMS
    # --------------------------

    meal_form = MealLogForm()

    water_form = WaterLogForm()

    weight_form = WeightLogForm()


    # --------------------------

    # LOG FOOD
    # --------------------------

    if request.method == "POST" and "meal_submit" in request.POST:

        food_name = request.POST.get("food_name", "").strip()
        variant_id = request.POST.get("variant_id")
        meal_type = request.POST.get("meal_type")

        # Manual nutrition values
        manual_calories = request.POST.get("manual_calories")
        manual_protein = request.POST.get("manual_protein")
        manual_carbohydrates = request.POST.get("manual_carbohydrates")
        manual_fat = request.POST.get("manual_fat")
        manual_fiber = request.POST.get("manual_fiber")

        if not food_name or not meal_type:
            messages.error(
                request,
                "Please enter the food name and meal type."
            )
            return redirect("userdash")


        try:

            # =========================================
            # CASE 1: FOOD VARIANT SELECTED
            # =========================================

            if variant_id:

                variant = FoodVariant.objects.get(
                    id=variant_id
                )

                MealLog.objects.create(
                    user=request.user,
                    food=variant.food,
                    food_name=f"{variant.food.name} - {variant.name}",
                    meal_type=meal_type,
                    quantity=1,
                    calories=variant.calories,
                    protein=variant.protein,
                    carbohydrates=variant.carbohydrates,
                    fat=variant.fat,
                    fiber=variant.fiber,
                    consumed_at=timezone.now(),
                )

                messages.success(
                    request,
                    f"{variant.food.name} - {variant.name} logged successfully!"
                )

                return redirect("userdash")


            # =========================================
            # CASE 2: PREVIOUSLY SAVED CUSTOM FOOD
            # =========================================

            previous_custom_food = MealLog.objects.filter(
                user=request.user,
                food__isnull=True,
                food_name__iexact=food_name
            ).order_by("-consumed_at").first()


            if previous_custom_food:

                MealLog.objects.create(
                    user=request.user,
                    food=None,
                    food_name=food_name,
                    meal_type=meal_type,
                    quantity=1,
                    calories=previous_custom_food.calories,
                    protein=previous_custom_food.protein,
                    carbohydrates=previous_custom_food.carbohydrates,
                    fat=previous_custom_food.fat,
                    fiber=previous_custom_food.fiber,
                    consumed_at=timezone.now(),
                )

                messages.success(
                    request,
                    f"{food_name} logged successfully using your saved nutrition!"
                )

                return redirect("userdash")


            # =========================================
            # CASE 3: COMPLETELY NEW MANUAL FOOD
            # =========================================

            if not manual_calories:

                messages.error(
                    request,
                    "Please enter the calories for this food."
                )

                return redirect("userdash")


            MealLog.objects.create(
                user=request.user,
                food=None,
                food_name=food_name,
                meal_type=meal_type,
                quantity=1,
                calories=float(manual_calories),
                protein=float(manual_protein or 0),
                carbohydrates=float(manual_carbohydrates or 0),
                fat=float(manual_fat or 0),
                fiber=float(manual_fiber or 0),
                consumed_at=timezone.now(),
            )

            messages.success(
                request,
                f"{food_name} logged successfully!"
            )

            return redirect("userdash")


        except FoodVariant.DoesNotExist:

            messages.error(
                request,
                "Selected food option was not found."
            )

            return redirect("userdash")

# --------------------------
    # --------------------------
    # LOG WATER
    # --------------------------

    elif request.method == "POST" and "water_submit" in request.POST:

        water_form = WaterLogForm(request.POST)

        if water_form.is_valid():

            water = water_form.save(
                commit=False
            )

            water.user = request.user

            water.save()

            messages.success(
                request,
                "Water logged successfully!"
            )

            return redirect("userdash")


    # --------------------------
    # LOG WEIGHT
    # --------------------------

    elif request.method == "POST" and "weight_submit" in request.POST:

        weight_form = WeightLogForm(request.POST)

        if weight_form.is_valid():

            weight = weight_form.save(
                commit=False
            )

            weight.user = request.user

            weight.save()

            messages.success(
                request,
                "Weight recorded successfully!"
            )

            return redirect("userdash")


    # --------------------------
    # RECENT ACTIVITY
    # --------------------------

    recent_meals = MealLog.objects.filter(
        user=request.user
    ).order_by(
        "-consumed_at"
    )[:5]
        # =========================================
    # TODAY'S NUTRITION TOTALS
    # =========================================

    today = timezone.localdate()

    today_meals = MealLog.objects.filter(
        user=request.user,
        consumed_at__date=today
    )

    today_calories = sum(
        meal.calories for meal in today_meals
    )

    today_protein = sum(
        meal.protein for meal in today_meals
    )

    today_carbohydrates = sum(
        meal.carbohydrates for meal in today_meals
    )

    today_fat = sum(
        meal.fat for meal in today_meals
    )

    today_fiber = sum(
        meal.fiber for meal in today_meals
    )


    recent_water = WaterLog.objects.filter(
        user=request.user
    ).order_by(
        "-consumed_at"
    )[:5]


    recent_weight = WeightLog.objects.filter(
        user=request.user
    ).order_by(
        "-recorded_at"
    )[:5]
    
    custom_foods = MealLog.objects.filter(
        user=request.user,
        food__isnull=True
    ).order_by("-consumed_at")

    # --------------------------
    # DASHBOARD CONTEXT
    # --------------------------

    context = {

        "meal_form": meal_form,

        "water_form": water_form,

        "weight_form": weight_form,

        "recent_meals": recent_meals,

        "recent_water": recent_water,

        "recent_weight": recent_weight,
        
        "foods": Food.objects.prefetch_related("variants"),
            
        "custom_foods": custom_foods,
        
        "today_calories": today_calories,
        
        "today_protein": today_protein,
        
        "today_carbohydrates": today_carbohydrates,
        
        "today_fat": today_fat,
        
        "today_fiber": today_fiber,

        "profile": profile,
        
        "baseline": baseline,
        
        "bmr": baseline["bmr"] if baseline else None,
        
        "tdee": baseline["tdee"] if baseline else None,

    }


    return render(
        request,
        "userdash.html",
        context
    )


# ==========================
# USER PROFILE
# ==========================

@login_required
def profilesetup(request):

    # Block admin/staff users
    if request.user.is_staff or request.user.is_superuser:

        return redirect("userdash")


    try:

        profile = UserProfile.objects.get(
            user=request.user
        )

    except UserProfile.DoesNotExist:

        profile = None


    if request.method == "POST":

        form = UserProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            profile = form.save(
                commit=False
            )

            profile.user = request.user

            profile.save()
            form.save_m2m()

            messages.success(
                request,
                "Profile saved successfully!"
            )

            return redirect("userdash")

    else:

        form = UserProfileForm(
            instance=profile
        )


    return render(
        request,
        "profilesetup.html",
        {"form": form}
    )


# ==========================
# SEPARATE LOGGING VIEWS
# ==========================
# These can stay for now.
# Our dashboard uses its own forms.


@login_required
def log_meal(request):

    if request.method == "POST":

        form = MealLogForm(request.POST)

        if form.is_valid():

            meal = form.save(
                commit=False
            )

            meal.user = request.user

            meal.save()

            messages.success(
                request,
                "Meal logged successfully!"
            )

            return redirect("userdash")

    else:

        form = MealLogForm()


    return render(
        request,
        "log_meal.html",
        {"form": form}
    )


@login_required
def log_water(request):

    if request.method == "POST":

        form = WaterLogForm(request.POST)

        if form.is_valid():

            water = form.save(
                commit=False
            )

            water.user = request.user

            water.save()

            messages.success(
                request,
                "Water entry logged successfully!"
            )

            return redirect("userdash")

    else:

        form = WaterLogForm()


    return render(
        request,
        "log_water.html",
        {"form": form}
    )


@login_required
def log_weight(request):

    if request.method == "POST":

        form = WeightLogForm(request.POST)

        if form.is_valid():

            weight = form.save(
                commit=False
            )

            weight.user = request.user

            weight.save()

            messages.success(
                request,
                "Weight entry recorded successfully!"
            )

            return redirect("userdash")

    else:

        form = WeightLogForm()


    return render(
        request,
        "log_weight.html",
        {"form": form}
    )


# ==========================
# FOOD MANAGEMENT
# ==========================

@login_required
def add_food(request):

    if request.method == "POST":

        form = FoodForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Food item created!"
            )

            return redirect("food_list")

    else:

        form = FoodForm()


    return render(
        request,
        "add_food.html",
        {"form": form}
    )


@login_required
def food_list(request):

    foods = Food.objects.all().select_related(
        "category"
    )

    return render(
        request,
        "food_list.html",
        {"foods": foods}
    )


@login_required
def add_category(request):

    if request.method == "POST":

        form = FoodCategoryForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Category created successfully!"
            )

            return redirect("add_food")

    else:

        form = FoodCategoryForm()


    return render(
        request,
        "add_category.html",
        {"form": form}
    )



# ==========================
# EDIT USER PROFILE
# ==========================

@login_required
def edit_profile(request):

    profile = request.user.userprofile

    if request.method == "POST":

        user_form = UserEditForm(
            request.POST,
            instance=request.user
        )

        profile_form = ProfileEditForm(
            request.POST,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            return redirect("userdash")

    else:

        user_form = UserEditForm(
            instance=request.user
        )

        profile_form = ProfileEditForm(
            instance=profile
        )

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(
        request,
        "edit_profile.html",
        context
    )


# ==========================
# USER PROFILE view
# ==========================

@login_required
def profile(request):
    profile = request.user.userprofile

    return render(request, "profile.html", {
        "profile": profile,
    })
