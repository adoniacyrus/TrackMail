from rest_framework import serializers


class DashboardStatisticsSerializer(serializers.Serializer):

    total_emails = serializers.IntegerField()

    sent_emails = serializers.IntegerField()

    failed_emails = serializers.IntegerField()

    opened_emails = serializers.IntegerField()

    total_open_events = serializers.IntegerField()