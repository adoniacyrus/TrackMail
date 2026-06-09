from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):

    return render(
        request,
        'dashboard/dashboard.html'
    )


@login_required
def compose_email_view(request):

    return render(
        request,
        'dashboard/compose.html'
    )