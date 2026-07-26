from django.contrib import admin

from .models import Membership, MembershipDecision


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "member_type", "relationship", "status", "updated_at")
    list_filter = ("member_type", "relationship", "status")
    search_fields = ("user__email", "relationship_note", "motivation")
    readonly_fields = ("submitted_at", "decided_at", "created_at", "updated_at")


@admin.register(MembershipDecision)
class MembershipDecisionAdmin(admin.ModelAdmin):
    list_display = ("membership", "from_status", "to_status", "actor", "created_at")
    list_filter = ("from_status", "to_status")
    search_fields = ("membership__user__email", "actor__email", "note")
    readonly_fields = (
        "membership",
        "actor",
        "from_status",
        "to_status",
        "note",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
