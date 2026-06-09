from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from apps.emails.models import Email
from apps.tracking.models import EmailOpenEvent


def track_email_open(request, tracking_id):
    """
    Tracking pixel endpoint.
    Records email open events.
    """

    email = get_object_or_404(
        Email,
        tracking_id=tracking_id
    )

    EmailOpenEvent.objects.create(
        email=email,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    pixel = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00'
        b'\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21'
        b'\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
        b'\x01\x00\x3b'
    )

    return HttpResponse(
        pixel,
        content_type='image/gif'
    )


def get_client_ip(request):
    """
    Extract client IP address.
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]

    return request.META.get('REMOTE_ADDR')