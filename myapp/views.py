from django.shortcuts import render
def home(request):
    return render(request, "home.html")
def index(request):
    return render(request, "index.html")
def about(request):
    return render(request, "about.html")
def contact(request):
    return render(request, "contact.html")



def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def register(request):
    return render(request, "register.html")

def user_login(request):
    return render(request, "login.html")

def user_logout(request):
    pass

# Create your views here.
