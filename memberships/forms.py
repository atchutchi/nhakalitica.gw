from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Membership


class MembershipApplicationForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = (
            "member_type",
            "relationship",
            "relationship_note",
            "motivation",
            "accepts_code_of_conduct",
            "accepts_privacy",
            "confirms_truth",
        )
        labels = {
            "member_type": _("Tipo de adesão"),
            "relationship": _("Ligação à Guiné-Bissau"),
            "relationship_note": _("Explica a ligação relevante"),
            "motivation": _("Motivação para aderir"),
        }
        widgets = {
            "member_type": forms.RadioSelect,
            "relationship": forms.RadioSelect,
            "relationship_note": forms.Textarea(attrs={"rows": 4}),
            "motivation": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("member_type", "relationship"):
            self.fields[field_name].choices = [
                choice for choice in self.fields[field_name].choices if choice[0]
            ]
        for field_name in (
            "accepts_code_of_conduct",
            "accepts_privacy",
            "confirms_truth",
        ):
            self.fields[field_name].required = True

    def clean(self):
        cleaned = super().clean()
        if (
            cleaned.get("relationship") == Membership.Relationship.RELEVANT_LINK
            and not cleaned.get("relationship_note", "").strip()
        ):
            self.add_error(
                "relationship_note",
                _("Explica a tua ligação relevante à Guiné-Bissau."),
            )
        return cleaned
