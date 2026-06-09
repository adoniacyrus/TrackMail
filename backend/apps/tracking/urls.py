from django.urls import path

from apps.tracking.views import track_email_open


urlpatterns = [
    path(
        'track/<uuid:tracking_id>/',
        track_email_open,
        name='track-email-open',
    ),
]