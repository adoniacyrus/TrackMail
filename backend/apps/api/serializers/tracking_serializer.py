from rest_framework import serializers

from apps.tracking.models import EmailOpenEvent


class EmailOpenEventSerializer(serializers.ModelSerializer):

    class Meta:

        model = EmailOpenEvent

        fields = [
            'id',
            'ip_address',
            'user_agent',
            'opened_at',
        ]