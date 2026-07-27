from django.shortcuts import render
def home(request):
    return render(request, "base.html")
def index(request):
    return render(request, "index.html")


# Create your views here.
