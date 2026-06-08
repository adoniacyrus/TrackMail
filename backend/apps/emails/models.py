import uuid

from django.conf import settings
from django.db import models


class EmailStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'


class Email(models.Model):
    """
    Stores emails sent through the system.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_emails'
    )

    recipient_email = models.EmailField()

    subject = models.CharField(max_length=255)

    body = models.TextField()

    tracking_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.subject} -> {self.recipient_email}"