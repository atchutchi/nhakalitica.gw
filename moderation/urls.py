from django.urls import path

from .views import (
    audit_list,
    dashboard,
    membership_list,
    membership_review,
    profile_list,
    profile_review,
    report_list,
    report_review,
)


app_name = "moderation"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("adesoes/", membership_list, name="membership-list"),
    path("adesoes/<int:pk>/", membership_review, name="membership-review"),
    path("perfis/", profile_list, name="profile-list"),
    path("perfis/<int:pk>/", profile_review, name="profile-review"),
    path("auditoria/", audit_list, name="audit-list"),
    path("denuncias/", report_list, name="report-list"),
    path("denuncias/<int:pk>/", report_review, name="report-review"),
]
