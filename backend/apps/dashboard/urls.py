from django.urls import path

from apps.dashboard.views import (
    compose_email_view,
    dashboard_view,
)

urlpatterns = [

    path(
        '',
        dashboard_view,
        name='dashboard',
    ),

    path(
        'compose/',
        compose_email_view,
        name='compose-email',
    ),
]