from django.urls import path

from .views import (
    about,
    code_of_conduct,
    health,
    home,
    how_it_works,
    membership_types,
    privacy,
    robots,
    terms,
)


urlpatterns = [
    path("", home, name="home"),
    path("sobre/", about, name="about"),
    path("tipos-de-adesao/", membership_types, name="membership-types"),
    path("como-funciona/", how_it_works, name="how-it-works"),
    path("termos/", terms, name="terms"),
    path("privacidade/", privacy, name="privacy"),
    path("codigo-de-conduta/", code_of_conduct, name="code-of-conduct"),
    path("robots.txt", robots, name="robots"),
    path("saude/", health, name="health"),
]
