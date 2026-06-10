from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.emails.models import Email
from apps.tracking.models import EmailOpenEvent
from apps.emails.tasks import send_tracking_email_task
from apps.dashboard.services.analytics_service import (
    get_dashboard_statistics
)


def landing_page_view(request):
    """
    Public landing page. Redirects to dashboard if authenticated.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'dashboard/landing.html')


@login_required
def dashboard_view(request):
    """
    User dashboard with statistics and recent activity.
    """
    user = request.user
    stats = get_dashboard_statistics(user)

    # Fetch 5 most recent emails
    recent_emails = Email.objects.filter(
        sender=user
    ).order_by('-created_at')[:5]

    # Fetch 5 most recent open events
    recent_events = EmailOpenEvent.objects.filter(
        email__sender=user
    ).order_by('-opened_at')[:5]

    context = {
        **stats,
        'recent_emails': recent_emails,
        'recent_events': recent_events,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )


@login_required
def compose_email_view(request):
    """
    Compose and send email page.
    """
    return render(
        request,
        'dashboard/compose.html'
    )


@login_required
def email_history_view(request):
    """
    Sent emails log page with search and pagination.
    """
    user = request.user
    query = request.GET.get('q', '').strip()

    emails = Email.objects.filter(sender=user).order_by('-created_at')

    if query:
        emails = emails.filter(
            Q(recipient_email__icontains=query) |
            Q(subject__icontains=query)
        )

    # Paginate by 10 emails per page
    paginator = Paginator(emails, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }

    return render(
        request,
        'dashboard/emails.html',
        context
    )


@login_required
def email_detail_view(request, pk):
    """
    Email detailed view including list of open events.
    """
    user = request.user
    email = get_object_or_404(
        Email,
        pk=pk,
        sender=user
    )

    open_events = email.open_events.all().order_by('-opened_at')

    context = {
        'email': email,
        'open_events': open_events,
        'open_count': open_events.count(),
    }

    return render(
        request,
        'dashboard/email_detail.html',
        context
    )


@login_required
def analytics_view(request):
    """
    Aggregated email analytics view.
    """
    user = request.user
    emails = Email.objects.filter(sender=user)
    total_emails = emails.count()
    opened_emails = emails.filter(
        open_events__isnull=False
    ).distinct().count()

    open_rate = (
        (opened_emails / total_emails * 100)
        if total_emails > 0
        else 0
    )

    # User's recent open events
    open_events = EmailOpenEvent.objects.filter(
        email__sender=user
    ).order_by('-opened_at')

    # Daily opens statistics (last 30 days) for Chart
    daily_opens = (
        open_events
        .annotate(date=TruncDate('opened_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    context = {
        'total_emails': total_emails,
        'opened_emails': opened_emails,
        'open_rate': round(open_rate, 1),
        'open_events': open_events,
        'daily_opens': list(daily_opens),
    }

    return render(
        request,
        'dashboard/analytics.html',
        context
    )


@login_required
@require_POST
def email_resend_view(request, pk):
    """
    Clones and re-queues an email for resending.
    """
    parent_email = get_object_or_404(
        Email,
        pk=pk,
        sender=request.user
    )

    # Clone the email into a new record with a new tracking identifier
    new_email = Email.objects.create(
        sender=request.user,
        recipient_email=parent_email.recipient_email,
        subject=parent_email.subject,
        body=parent_email.body
    )

    # Queue via Celery task
    send_tracking_email_task.delay(new_email.id)

    # Add alert feedback message
    messages.success(request, "Email queued for resend successfully.")

    return redirect('email-history')