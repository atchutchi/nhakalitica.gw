from django.contrib import admin

from .models import Certification, Education, Experience, Profile, ProfileLanguage, ProfileRevision


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("public_name", "user", "professional_title", "status", "is_public")
    list_filter = ("status", "is_public")
    search_fields = ("public_name", "user__email", "professional_title", "search_keywords", "location")
    filter_horizontal = ("specializations", "skills")
    readonly_fields = ("approved_at", "reviewed_at", "reviewed_by", "review_note", "created_at", "updated_at")


admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Certification)
admin.site.register(ProfileLanguage)


@admin.register(ProfileRevision)
class ProfileRevisionAdmin(admin.ModelAdmin):
    list_display = ("profile", "status", "submitted_by", "submitted_at", "reviewed_by", "reviewed_at")
    list_filter = ("status", "submitted_at")
    search_fields = ("profile__public_name", "profile__user__email", "submitted_by__email")
    readonly_fields = (
        "profile",
        "submitted_by",
        "payload",
        "status",
        "review_note",
        "reviewed_by",
        "submitted_at",
        "reviewed_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
