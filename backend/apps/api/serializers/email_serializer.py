from rest_framework import serializers

from apps.emails.models import Email


class EmailSerializer(serializers.ModelSerializer):

    open_count = serializers.SerializerMethodField()

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
            'open_count',
        ]

        read_only_fields = [
            'tracking_id',
            'status',
            'created_at',
            'sent_at',
            'open_count',
        ]

    def get_open_count(self, obj):

        return obj.open_events.count()