import logging
from django.http import HttpResponse
from apps.emails.models import Email
from apps.tracking.models import EmailOpenEvent

logger = logging.getLogger('apps.tracking')


def is_prefetch_request(request):
    """
    Lightweight detection of email client prefetching or bots.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()

    # Check common prefetch headers
    purpose = request.META.get('HTTP_PURPOSE', '').lower()
    x_purpose = request.META.get('HTTP_X_PURPOSE', '').lower()
    x_moz = request.META.get('HTTP_X_MOZ', '').lower()
    sec_purpose = request.META.get('HTTP_SEC_PURPOSE', '').lower()

    if 'prefetch' in [purpose, x_purpose, x_moz, sec_purpose]:
        return True

    # Check for bots or prefetching crawlers
    suspicious_patterns = [
        'prefetch', 'preview', 'bot', 'spider', 'crawler',
        'yahooimageproxy', 'googleimageproxy', 'office365-imageproxy', 'bingpreview'
    ]
    for pattern in suspicious_patterns:
        if pattern in user_agent:
            return True

    return False


def track_email_open(request, tracking_id):
    """
    Tracking pixel endpoint.
    Records email open events.
    """
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_prefetch = is_prefetch_request(request)

    # Logging tracking details
    logger.info(
        f"Tracking Pixel Request: ID={tracking_id} | "
        f"IP={ip_address} | "
        f"UA={user_agent} | "
        f"Prefetch={is_prefetch}"
    )

    try:
        # Look up email. Fail silently if not found or if database errors occur.
        email = Email.objects.filter(tracking_id=tracking_id).first()
        if email:
            EmailOpenEvent.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                is_prefetch=is_prefetch
            )
    except Exception as error:
        # Fail silently if database/analytics operations fail
        logger.error(f"Error recording open event for tracking ID {tracking_id}: {error}")

    pixel = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00'
        b'\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21'
        b'\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
        b'\x01\x00\x3b'
    )

    response = HttpResponse(
        pixel,
        content_type='image/gif'
    )

    # Disable caching response headers
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


def get_client_ip(request):
    """
    Extract client IP address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')