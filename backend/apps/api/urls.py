from django.urls import path

from apps.api.views.dashboard_views import (
    DashboardStatisticsAPIView
)
from apps.api.views.email_views import (
    EmailListCreateAPIView
)
from apps.api.views.tracking_views import (
    TrackingEventListAPIView
)
from apps.api.views.live_views import (
    dashboard_stats_api_view,
    email_stats_api_view,
)

urlpatterns = [

    path(
        'emails/',
        EmailListCreateAPIView.as_view(),
        name='api-emails',
    ),

    path(
        'dashboard/',
        DashboardStatisticsAPIView.as_view(),
        name='api-dashboard',
    ),

    path(
        'tracking-events/',
        TrackingEventListAPIView.as_view(),
        name='api-tracking-events',
    ),

    path(
        'email/<int:pk>/stats/',
        email_stats_api_view,
        name='api-email-stats',
    ),

    path(
        'dashboard/stats/',
        dashboard_stats_api_view,
        name='api-dashboard-stats',
    ),
]