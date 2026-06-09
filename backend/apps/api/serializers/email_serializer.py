from rest_framework import serializers

from apps.emails.models import Email


class EmailSerializer(serializers.ModelSerializer):

    class Meta:

        model = Email

        fields = [
            'id',
            'recipient_email',
            'subject',
            'body',
            'tracking_id',
            'status',
            'created_at',
            'sent_at',
        ]

        read_only_fields = [
            'tracking_id',
            'status',
            'created_at',
            'sent_at',
        ]