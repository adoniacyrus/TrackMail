import uuid
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from apps.emails.models import Email, EmailStatus


def generate_tracking_pixel(tracking_id):
    """
    Generates invisible tracking pixel HTML.
    """

    tracking_url = (
        f"{settings.SITE_URL}"
        f"/track/{tracking_id}/"
        f"?r={uuid.uuid4().hex}"
    )

    return f"""
        <img
            src="{tracking_url}"
            width="1"
            height="1"
            style="display:none;"
            alt=""
        />
    """


def send_tracking_email(email: Email):
    """
    Sends tracking-enabled HTML email.
    """

    tracking_pixel = generate_tracking_pixel(
        email.tracking_id
    )

    html_content = f"""
        <html>
            <body>
                {email.body}

                {tracking_pixel}
            </body>
        </html>
    """

    try:

        message = EmailMultiAlternatives(
            subject=email.subject,
            body='HTML email not supported.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email.recipient_email],
        )

        message.attach_alternative(
            html_content,
            "text/html"
        )

        message.send()

        email.status = EmailStatus.SENT

        email.sent_at = timezone.now()

        email.save()

        return True

    except Exception as error:

        email.status = EmailStatus.FAILED

        email.save()

        print(f"Email sending failed: {error}")

        return False