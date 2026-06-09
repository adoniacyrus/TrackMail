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
]