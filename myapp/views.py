# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages


# def home(request):
#     return render(request, "home.html")


# def index(request):
#     return render(request, "index.html")


# def about(request):
#     return render(request, "about.html")


# def contact(request):
#     return render(request, "contact.html")



# # Registration
# def register(request):

#     if request.method == "POST":

#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password1 = request.POST.get("password1")
#         password2 = request.POST.get("password2")


#         if password1 != password2:
#             messages.error(request, "Passwords do not match")
#             return redirect("register")


#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists")
#             return redirect("register")


#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password1
#         )

#         user.save()

#         messages.success(request, "Account created successfully")

#         return redirect("login")


#     return render(request, "register.html")



# # Login
# def user_login(request):

#     if request.method == "POST":

#         username = request.POST.get("username")
#         password = request.POST.get("password")


#         user = authenticate(
#             request,
#             username=username,
#             password=password
#         )


#         if user is not None:

#             login(request, user)

#             return redirect("userdash")

#         else:

#             messages.error(
#                 request,
#                 "Invalid username or password"
#             )

#             return redirect("login")


#     return render(request, "login.html")



# # Logout
# def user_logout(request):

#     logout(request)

#     return redirect("index")


# def userdash(request):
#     return render(request, "userdash.html")




from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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

            messages.error(
                request,
                "Passwords do not match"
            )

            return redirect("register")



        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

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


            login(
                request,
                user
            )


            return redirect("userdash")



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

    return render(
        request,
        "userdash.html"
    )