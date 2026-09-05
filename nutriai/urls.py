"""
URL configuration for nutriai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp import api

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # REST API Endpoints
    path('api/users/login/', api.api_login, name='api_login'),
    path('api/users/register/', api.api_register, name='api_register'),
    path('api/nutrition/foods/', api.api_foods, name='api_foods'),
    path('api/recommendations/', api.api_recommendations, name='api_recommendations'),
    path('api/assistant/chat/', api.api_chat, name='api_chat'),

    # Template Pages & Views
    path("", include("myapp.urls")),
]
