from django.db import models

from apps.emails.models import Email


class EmailOpenEvent(models.Model):
    """
    Stores each email open event.
    """

    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        related_name='open_events'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        null=True,
        blank=True
    )

    opened_at = models.DateTimeField(
        auto_now_add=True
    )

    # Future-proof Geolocation fields
    country = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    region = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.email.subject} opened at {self.opened_at}"