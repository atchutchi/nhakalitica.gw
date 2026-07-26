from hashlib import sha256

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from moderation.models import AuditLog
from interactions.models import Favorite, SavedSearch
from profiles.models import Profile

from .forms import AccountForm, PasswordConfirmationForm, SignUpForm
from .models import User
from .services import send_verification_email
from .tokens import email_verification_token


class ThrottledLoginView(LoginView):
    failure_limit = 5
    lock_seconds = 15 * 60

    def throttle_key(self):
        email = self.request.POST.get("username", "").strip().lower()
        address = self.request.META.get("REMOTE_ADDR", "")
        digest = sha256(f"{email}:{address}".encode()).hexdigest()
        return f"login-failures:{digest}"

    def post(self, request, *args, **kwargs):
        key = self.throttle_key()
        failures = cache.get(key, 0)
        if failures >= self.failure_limit:
            form = self.get_form()
            form.add_error(None, "Demasiadas tentativas. Tenta novamente dentro de 15 minutos.")
            return self.form_invalid(form)
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            cache.delete(key)
        else:
            cache.set(key, failures + 1, self.lock_seconds)
        return response


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        send_verification_email(request, user)
        messages.info(request, "Enviámos uma ligação para confirmares o teu email.")
        return redirect("accounts:dashboard")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    return render(
        request,
        "accounts/dashboard.html",
        {
            "recent_saved_searches": SavedSearch.objects.filter(user=request.user)[:5],
            "shortlist_count": Favorite.objects.filter(user=request.user).count(),
        },
    )


@login_required
def resend_verification(request):
    if request.method == "POST" and not request.user.email_verified_at:
        send_verification_email(request, request.user)
        messages.success(request, "Enviámos uma nova ligação de confirmação.")
    return redirect("accounts:dashboard")


def verify_email(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and email_verification_token.check_token(user, token):
        user.email_verified_at = timezone.now()
        user.save(update_fields=("email_verified_at",))
        messages.success(request, "Email confirmado com sucesso.")
        if not request.user.is_authenticated:
            login(request, user)
        return redirect("accounts:dashboard")
    return render(request, "accounts/verification_invalid.html", status=200)


@login_required
def edit_account(request):
    previous_email = request.user.email
    form = AccountForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        email_changed = user.email.lower() != previous_email.lower()
        if email_changed:
            user.email_verified_at = None
        user.save()
        if email_changed:
            send_verification_email(request, user)
            messages.info(request, "Confirma o novo endereço de email.")
        else:
            messages.success(request, "Dados da conta actualizados.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/edit.html", {"form": form})


@login_required
def deactivate_account(request):
    form = PasswordConfirmationForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = request.user
        profile = user.profile
        profile.is_public = False
        profile.status = Profile.Status.ARCHIVED
        profile.save(update_fields=("is_public", "status", "updated_at"))
        AuditLog.objects.create(
            actor=user,
            action="account.deactivated",
            target_type="user",
            target_id=str(user.pk),
            metadata={},
        )
        user.is_active = False
        user.save(update_fields=("is_active",))
        logout(request)
        return redirect("accounts:login")
    return render(request, "accounts/deactivate.html", {"form": form})
