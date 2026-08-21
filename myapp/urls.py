# from django.urls import path
# from . import views
# urlpatterns = [
#     path("", views.index, name="index"),
#     path("index/", views.index, name="index"),
#     path("about/", views.about, name="about"),
#     path("home/", views.home, name="home"),
#     path("contact/", views.contact, name="contact"),
#     path("register/", views.register, name="register"),
#     path("login/", views.user_login, name="login"),
#     path("logout/", views.user_logout, name="logout"),
#     path("userdash/",views.userdash, name="userdash")

# ]



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

]