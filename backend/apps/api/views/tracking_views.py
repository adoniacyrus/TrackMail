from rest_framework import generics, permissions

from apps.api.serializers.tracking_serializer import (
    EmailOpenEventSerializer
)
from apps.tracking.models import EmailOpenEvent


class TrackingEventListAPIView(generics.ListAPIView):

    serializer_class = EmailOpenEventSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return EmailOpenEvent.objects.filter(
            email__sender=self.request.user
        ).order_by('-opened_at')