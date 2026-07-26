from django import forms

from .models import ContactRequest, Favorite, RecruitmentTag, Report, SavedSearch


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ("subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 7})}


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("reason", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class FavoriteUpdateForm(forms.ModelForm):
    tags = forms.CharField(required=False, max_length=500)

    def clean_tags(self):
        raw_tags = self.cleaned_data["tags"]
        for raw_name in raw_tags.split(","):
            name = " ".join(raw_name.split())
            normalized_name = RecruitmentTag.objects.normalise_name(name)
            if name and (len(name) > 80 or len(normalized_name) > 80):
                raise forms.ValidationError("Cada etiqueta pode ter no máximo 80 caracteres.")
        return raw_tags

    class Meta:
        model = Favorite
        fields = ("status", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}


class SavedSearchForm(forms.ModelForm):
    class Meta:
        model = SavedSearch
        fields = ("name",)
