from django.urls import path

from .views import area_detail, area_list


urlpatterns = [
    path("areas/", area_list, name="area-list"),
    path("areas/<slug:slug>/", area_detail, name="area-detail"),
]
