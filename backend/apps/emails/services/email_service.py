from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_tracking_email(
    subject,
    recipient_email,
    html_content,
):
    """
    Sends HTML email through Brevo SMTP.
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body='HTML email not supported.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )

    email.attach_alternative(html_content, "text/html")

    email.send()

    return True