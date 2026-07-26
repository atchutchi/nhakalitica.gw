from django.urls import path

from .views import (
    contact,
    contact_action,
    contacts,
    compare,
    favorite_add,
    favorite_toggle,
    favorite_update,
    favorites,
    like_toggle,
    notification_read,
    notifications,
    report,
    saved_search_create,
    saved_search_delete,
    saved_search_run,
    shortlist_export,
)


app_name = "interactions"

urlpatterns = [
    path("favoritos/", favorites, name="favorites"),
    path("favoritos/<int:pk>/actualizar/", favorite_update, name="favorite-update"),
    path("favoritos/<slug:slug>/adicionar/", favorite_add, name="favorite-add"),
    path("favoritos/<slug:slug>/alternar/", favorite_toggle, name="favorite-toggle"),
    path("pesquisas/guardar/", saved_search_create, name="saved-search-create"),
    path("pesquisas/<int:pk>/executar/", saved_search_run, name="saved-search-run"),
    path("pesquisas/<int:pk>/apagar/", saved_search_delete, name="saved-search-delete"),
    path("favoritos/comparar/", compare, name="compare"),
    path("favoritos/exportar/", shortlist_export, name="shortlist-export"),
    path("gostos/<slug:slug>/alternar/", like_toggle, name="like-toggle"),
    path("contactar/<slug:slug>/", contact, name="contact"),
    path("contactos/", contacts, name="contacts"),
    path("contactos/<int:pk>/acao/", contact_action, name="contact-action"),
    path("denunciar/<slug:slug>/", report, name="report"),
    path("notificacoes/", notifications, name="notifications"),
    path("notificacoes/<int:pk>/ler/", notification_read, name="notification-read"),
]
