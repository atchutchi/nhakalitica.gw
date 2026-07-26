from django.contrib import admin

from .models import ContactRequest, Favorite, Notification, ProfileLike, Report


admin.site.register(Favorite)
admin.site.register(ProfileLike)
admin.site.register(ContactRequest)
admin.site.register(Notification)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("profile", "reporter", "reason", "status", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("profile__public_name", "reporter__email", "description")
