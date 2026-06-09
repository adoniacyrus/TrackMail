from celery import shared_task

from apps.emails.models import Email
from apps.emails.services.email_service import (
    send_tracking_email
)


@shared_task
def send_tracking_email_task(email_id):

    email = Email.objects.get(id=email_id)

    send_tracking_email(email)