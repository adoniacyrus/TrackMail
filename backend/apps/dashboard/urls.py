from django.urls import path

from apps.dashboard.views import (
    landing_page_view,
    dashboard_view,
    compose_email_view,
    email_history_view,
    email_detail_view,
    analytics_view,
    email_resend_view,
)

urlpatterns = [
    path(
        '',
        landing_page_view,
        name='landing-page'
    ),
    path(
        'dashboard/',
        dashboard_view,
        name='dashboard'
    ),
    path(
        'compose/',
        compose_email_view,
        name='compose-email'
    ),
    path(
        'emails/',
        email_history_view,
        name='email-history'
    ),
    path(
        'emails/<int:pk>/',
        email_detail_view,
        name='email-detail'
    ),
    path(
        'emails/<int:pk>/resend/',
        email_resend_view,
        name='email-resend'
    ),
    path(
        'analytics/',
        analytics_view,
        name='analytics'
    ),
]