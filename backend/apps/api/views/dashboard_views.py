from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers.dashboard_serializer import (
    DashboardStatisticsSerializer
)
from apps.dashboard.services.analytics_service import (
    get_dashboard_statistics
)


class DashboardStatisticsAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        stats = get_dashboard_statistics(
            request.user
        )

        serializer = DashboardStatisticsSerializer(
            stats
        )

        return Response(serializer.data)