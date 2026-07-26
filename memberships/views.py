from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Membership


@login_required
def dashboard(request):
    membership, _created = Membership.objects.get_or_create(user=request.user)
    return render(
        request,
        "memberships/dashboard.html",
        {"membership": membership},
    )
