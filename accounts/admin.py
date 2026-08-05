from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from moderation.models import AuditLog

from .services import restore_scheduled_account
from .models import LegalAcceptance, User


@admin.register(LegalAcceptance)
class LegalAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("user", "document_type", "version", "source", "accepted_at")
    list_filter = ("document_type", "version", "source")
    search_fields = ("user__email",)
    readonly_fields = ("user", "document_type", "version", "source", "accepted_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    actions = ("restore_accounts_within_recovery_period",)
    readonly_fields = ("deletion_requested_at", "scheduled_deletion_at")
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informação pessoal", {"fields": ("first_name", "last_name")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Datas importantes",
            {
                "fields": (
                    "email_verified_at",
                    "deletion_requested_at",
                    "scheduled_deletion_at",
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    @admin.action(description="Restaurar contas dentro do prazo de recuperação")
    def restore_accounts_within_recovery_period(self, request, queryset):
        restored = 0
        for user in queryset.filter(
            is_active=False,
            scheduled_deletion_at__gt=timezone.now(),
        ):
            restore_scheduled_account(user)
            AuditLog.objects.create(
                actor=request.user,
                action="account.deletion_restored",
                target_type="user",
                target_id=str(user.pk),
                metadata={},
            )
            restored += 1
        self.message_user(request, f"{restored} conta(s) restaurada(s).")
