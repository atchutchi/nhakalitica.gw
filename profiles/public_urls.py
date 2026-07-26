from django.urls import path

from .public_views import profile_cv, profile_photo, public_profile, search


urlpatterns = [
    path("pesquisar/", search, name="search"),
    path("profissionais/<slug:slug>/", public_profile, name="public-profile"),
    path("profissionais/<slug:slug>/fotografia/", profile_photo, name="profile-photo"),
    path("profissionais/<slug:slug>/curriculo/", profile_cv, name="profile-cv"),
]
