from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import sitemaps


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("profiles.public_urls")),
    path("", include("taxonomy.urls")),
    path("", include("core.urls")),
    path("conta/", include("accounts.urls")),
    path("adesao/", include("memberships.urls")),
    path("perfil/", include("profiles.urls")),
    path("administracao/", include("moderation.urls")),
    path("interacoes/", include("interactions.urls")),
    path("admin/", admin.site.urls),
]
