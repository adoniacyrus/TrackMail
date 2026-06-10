from django.db.models import Count

from apps.emails.models import Email, EmailStatus
from apps.tracking.models import EmailOpenEvent


def get_dashboard_statistics(user):
    """
    Returns dashboard analytics data.
    """

    emails = Email.objects.filter(
        sender=user
    )

    total_emails = emails.count()

    sent_emails = emails.filter(
        status=EmailStatus.SENT
    ).count()

    failed_emails = emails.filter(
        status=EmailStatus.FAILED
    ).count()

    opened_emails = emails.filter(
        open_events__isnull=False
    ).distinct().count()

    total_open_events = EmailOpenEvent.objects.filter(
        email__sender=user
    ).count()

    # Get the latest open time
    latest_event = EmailOpenEvent.objects.filter(
        email__sender=user
    ).order_by('-opened_at').first()
    latest_open_time = latest_event.opened_at if latest_event else None

    # Get emails with repeated opens
    repeated_emails = emails.annotate(
        num_opens=Count('open_events')
    ).filter(
        num_opens__gt=1
    ).order_by('-num_opens')

    return {
        'total_emails': total_emails,
        'sent_emails': sent_emails,
        'failed_emails': failed_emails,
        'opened_emails': opened_emails,
        'total_open_events': total_open_events,
        'latest_open_time': latest_open_time,
        'repeated_emails': repeated_emails,
    }