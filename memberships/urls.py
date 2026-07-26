from django.urls import path

from .views import dashboard


app_name = "memberships"

urlpatterns = [
    path("", dashboard, name="dashboard"),
]
