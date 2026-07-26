from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse

from .models import Membership


def get_membership(user):
    if not user.is_authenticated:
        return None
    try:
        return user.membership
    except Membership.DoesNotExist:
        return None


def network_member_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        membership = get_membership(request.user)
        if not membership or not membership.can_access_network:
            return redirect("memberships:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapped


def membership_access_context(request):
    membership = get_membership(request.user)
    return {
        "current_membership": membership,
        "can_access_network": bool(
            membership and membership.can_access_network
        ),
        "membership_dashboard_url": reverse("memberships:dashboard"),
    }
