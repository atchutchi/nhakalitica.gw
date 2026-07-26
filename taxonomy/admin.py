from django.contrib import admin

from .models import Area, Sector, Skill, Specialization


class NamedActiveAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Sector)
class SectorAdmin(NamedActiveAdmin):
    pass


@admin.register(Area)
class AreaAdmin(NamedActiveAdmin):
    list_display = ("name", "sector", "is_active", "updated_at")
    list_filter = ("sector", "is_active")


@admin.register(Specialization)
class SpecializationAdmin(NamedActiveAdmin):
    list_display = ("name", "area", "is_active", "updated_at")
    list_filter = ("area", "is_active")


@admin.register(Skill)
class SkillAdmin(NamedActiveAdmin):
    filter_horizontal = ("specializations",)
