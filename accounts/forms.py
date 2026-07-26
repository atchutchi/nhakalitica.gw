from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class SignUpForm(UserCreationForm):
    country = forms.CharField(
        label=_("País de residência"),
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "country-name"}),
    )
    accept_terms = forms.BooleanField(
        label=_("Li e aceito os Termos de Utilização e a Política de Privacidade")
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        labels = {
            "email": "Email",
            "first_name": _("Nome"),
            "last_name": _("Apelido"),
        }
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Já existe uma conta com este email."))
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.country = self.cleaned_data["country"].strip()
            user.profile.save(update_fields=("country", "updated_at"))
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.email_verified_at:
            raise forms.ValidationError(
                _("Confirma o teu email antes de iniciares sessão."),
                code="email_not_verified",
            )


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        labels = {"email": "Email", "first_name": _("Nome"), "last_name": _("Apelido")}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("Já existe uma conta com este email."))
        return email


class PasswordConfirmationForm(forms.Form):
    password = forms.CharField(label=_("Palavra-passe actual"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError(_("A palavra-passe está incorrecta."))
        return password
