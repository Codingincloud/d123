from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

            UserProfile.objects.get(
                user=request.user
            )

        except UserProfile.DoesNotExist:

            return redirect("profilesetup")


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

        meal_form = MealLogForm(request.POST)

        if meal_form.is_valid():

            meal = meal_form.save(
                commit=False
            )

            meal.user = request.user

            meal.save()

            messages.success(
                request,
                "Meal logged successfully!"
            )

            return redirect("userdash")


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
