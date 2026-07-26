from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "target_type", "target_id")
    list_filter = ("action", "target_type", "created_at")
    search_fields = ("actor__email", "action", "target_type", "target_id")
    readonly_fields = ("actor", "action", "target_type", "target_id", "metadata", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and obj is not None

    def has_delete_permission(self, request, obj=None):
        return False
