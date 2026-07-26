from django.urls import path

from .views import add_section, delete_section, edit_profile, edit_section, preview_profile, submit_profile


app_name = "profiles"

urlpatterns = [
    path("editar/", edit_profile, name="edit"),
    path("submeter/", submit_profile, name="submit"),
    path("pre-visualizar/", preview_profile, name="preview"),
    path("secao/<slug:section>/adicionar/", add_section, name="section_add"),
    path("secao/<slug:section>/<int:pk>/eliminar/", delete_section, name="section_delete"),
    path("secao/<slug:section>/<int:pk>/editar/", edit_section, name="section_edit"),
]
