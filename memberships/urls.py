from django.urls import path

from .views import dashboard, edit, review, submit


app_name = "memberships"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("editar/", edit, name="edit"),
    path("rever/", review, name="review"),
    path("submeter/", submit, name="submit"),
]
