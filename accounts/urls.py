from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path

from .forms import EmailAuthenticationForm
from .views import (
    ThrottledLoginView,
    dashboard,
    deactivate_account,
    edit_account,
    resend_verification,
    signup,
    verify_email,
)


app_name = "accounts"

urlpatterns = [
    path("criar/", signup, name="signup"),
    path(
        "entrar/",
        ThrottledLoginView.as_view(
            template_name="registration/login.html",
            authentication_form=EmailAuthenticationForm,
        ),
        name="login",
    ),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("painel/", dashboard, name="dashboard"),
    path("editar/", edit_account, name="edit"),
    path("desactivar/", deactivate_account, name="deactivate"),
    path("confirmar-email/reenviar/", resend_verification, name="resend-verification"),
    path("confirmar-email/<uidb64>/<token>/", verify_email, name="verify-email"),
    path(
        "recuperar-palavra-passe/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
            success_url="/conta/recuperar-palavra-passe/enviado/",
        ),
        name="password_reset",
    ),
    path(
        "recuperar-palavra-passe/enviado/",
        PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "redefinir-palavra-passe/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/conta/redefinir-palavra-passe/concluido/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "redefinir-palavra-passe/concluido/",
        PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path(
        "alterar-palavra-passe/",
        PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/conta/alterar-palavra-passe/concluido/",
        ),
        name="password_change",
    ),
    path(
        "alterar-palavra-passe/concluido/",
        PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"),
        name="password_change_done",
    ),
]
