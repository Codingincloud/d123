


from django.urls import path
from . import views


urlpatterns = [

    path("", views.index, name="index"),

    path("home/", views.home, name="home"),

    path("about/", views.about, name="about"),

    path("contact/", views.contact, name="contact"),


    path("register/", views.register, name="register"),

    path("login/", views.user_login, name="login"),

    path("logout/", views.user_logout, name="logout"),

    path("dashboard/", views.userdash, name="userdash"),
    
    path("profile/setup/",views.profilesetup,name="profilesetup"),
    path('log-meal/', views.log_meal, name='log_meal'),
    path('log-water/', views.log_water, name='log_water'),
    path('log-weight/', views.log_weight, name='log_weight'),
    path("profile/edit/",views.edit_profile,name="edit_profile"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

]   