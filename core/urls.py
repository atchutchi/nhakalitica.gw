from django.urls import path

from .views import about, health, home, how_it_works, membership_types, robots


urlpatterns = [
    path("", home, name="home"),
    path("sobre/", about, name="about"),
    path("tipos-de-adesao/", membership_types, name="membership-types"),
    path("como-funciona/", how_it_works, name="how-it-works"),
    path("robots.txt", robots, name="robots"),
    path("saude/", health, name="health"),
]
