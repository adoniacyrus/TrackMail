from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince

from apps.emails.models import Email
from apps.tracking.models import EmailOpenEvent
from apps.dashboard.services.analytics_service import get_dashboard_statistics


def dashboard_stats_api_view(request):
    """
    Returns live statistics and recent activity for the authenticated user's dashboard.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    user = request.user
    stats = get_dashboard_statistics(user)

    latest_event = EmailOpenEvent.objects.filter(
        email__sender=user
    ).order_by('-opened_at').first()

    latest_open_formatted = None
    if latest_event:
        latest_open_formatted = {
            'time': latest_event.opened_at.strftime('%H:%M:%S'),
            'date': latest_event.opened_at.strftime('%b %d'),
            'iso': latest_event.opened_at.isoformat()
        }

    # Fetch 5 most recent emails
    recent_emails = Email.objects.filter(sender=user).order_by('-created_at')[:5]
    recent_emails_data = []
    for email in recent_emails:
        recent_emails_data.append({
            'id': email.id,
            'subject': email.subject,
            'recipient_email': email.recipient_email,
            'created_at_timesince': timesince(email.created_at),
            'status': email.status,
            'open_count': email.open_events.count(),
        })

    # Fetch 5 most recent open events
    recent_events = EmailOpenEvent.objects.filter(
        email__sender=user
    ).select_related('email').order_by('-opened_at')[:5]
    recent_events_data = []
    for event in recent_events:
        recent_events_data.append({
            'id': event.id,
            'email_id': event.email.id,
            'subject': event.email.subject,
            'recipient_email': event.email.recipient_email,
            'opened_at_iso': event.opened_at.isoformat(),
            'timesince': timesince(event.opened_at),
            'is_prefetch': event.is_prefetch or False,
            'ip_address': event.ip_address or 'Unknown',
        })

    # Fetch 5 repeated open emails
    repeated_emails = Email.objects.filter(sender=user).annotate(
        num_opens=Count('open_events')
    ).filter(
        num_opens__gt=1
    ).order_by('-num_opens')[:5]

    repeated_emails_data = []
    for email in repeated_emails:
        first_event = email.open_events.order_by('-opened_at').first()
        last_open_timesince = timesince(first_event.opened_at) if first_event else 'Unknown'
        repeated_emails_data.append({
            'id': email.id,
            'subject': email.subject,
            'recipient_email': email.recipient_email,
            'num_opens': email.num_opens,
            'last_open_timesince': last_open_timesince,
        })

    return JsonResponse({
        'total_emails': stats['total_emails'],
        'sent_emails': stats['sent_emails'],
        'failed_emails': stats['failed_emails'],
        'opened_emails': stats['opened_emails'],
        'total_open_events': stats['total_open_events'],
        'latest_open_time': latest_open_formatted,
        'recent_emails': recent_emails_data,
        'recent_events': recent_events_data,
        'repeated_emails': repeated_emails_data,
    })


def email_stats_api_view(request, pk):
    """
    Returns live statistics and the events timeline for a specific email.
    Only accessible by the owner of the email.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    email = get_object_or_404(Email, pk=pk)
    if email.sender != request.user:
        return JsonResponse({'error': 'Permission denied.'}, status=403)

    open_events = email.open_events.all().order_by('opened_at')
    total_opens_count = open_events.count()
    unique_opens_count = email.open_events.values('ip_address').distinct().count()

    latest_event = open_events.order_by('-opened_at').first()
    latest_open_formatted = None
    if latest_event:
        latest_open_formatted = {
            'time': latest_event.opened_at.strftime('%H:%M:%S'),
            'date': latest_event.opened_at.strftime('%b %d'),
            'iso': latest_event.opened_at.isoformat()
        }

    events_data = []
    for idx, event in enumerate(open_events, 1):
        events_data.append({
            'counter': idx,
            'id': event.id,
            'opened_at_iso': event.opened_at.isoformat(),
            'opened_at_formatted': event.opened_at.strftime('%Y-%m-%d %H:%M:%S'),
            'timesince': timesince(event.opened_at),
            'ip_address': event.ip_address or 'Unknown',
            'user_agent': event.user_agent or 'Unknown',
            'is_prefetch': event.is_prefetch or False,
        })

    return JsonResponse({
        'email_id': email.id,
        'open_count': total_opens_count,
        'unique_opens_count': unique_opens_count,
        'latest_open_time': latest_open_formatted,
        'events': events_data,
    })
