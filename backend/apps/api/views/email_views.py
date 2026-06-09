from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.api.serializers.email_serializer import EmailSerializer
from apps.emails.models import Email
from apps.emails.services.email_service import send_tracking_email


class EmailListCreateAPIView(generics.ListCreateAPIView):

    serializer_class = EmailSerializer

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        return Email.objects.filter(
            sender=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):

        email = serializer.save(
            sender=self.request.user
        )

        send_tracking_email(email)

    def create(self, request, *args, **kwargs):

        response = super().create(request, *args, **kwargs)

        return Response(
            {
                'message': 'Email sent successfully.',
                'data': response.data
            },
            status=status.HTTP_201_CREATED
        )