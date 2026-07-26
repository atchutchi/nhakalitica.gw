from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from profiles.selectors import public_profiles
from taxonomy.models import Area


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ("home", "area-list")

    def location(self, item):
        return reverse(item)


class ProfileSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return public_profiles()

    def location(self, profile):
        return reverse("public-profile", args=(profile.slug,))

    def lastmod(self, profile):
        return profile.published_at or profile.updated_at


class AreaSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Area.objects.filter(is_active=True)

    def location(self, area):
        return reverse("area-detail", args=(area.slug,))


sitemaps = {"static": StaticSitemap, "profiles": ProfileSitemap, "areas": AreaSitemap}
