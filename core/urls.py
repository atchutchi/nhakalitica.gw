from django.urls import path

from .views import health, home, robots


urlpatterns = [
    path("", home, name="home"),
    path("robots.txt", robots, name="robots"),
    path("saude/", health, name="health"),
]
