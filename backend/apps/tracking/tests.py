import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.emails.models import Email, EmailStatus
from apps.tracking.models import EmailOpenEvent

User = get_user_model()


class EmailTrackingTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.email = Email.objects.create(
            sender=self.user,
            recipient_email='recipient@example.com',
            subject='Test Email Subject',
            body='Hello, this is a test email body.'
        )

    def test_track_email_open_success(self):
        """
        Verify that a valid tracking ID creates an EmailOpenEvent,
        returns HTTP 200 with GIF, and sets caching headers.
        """
        url = reverse('track-email-open', kwargs={'tracking_id': self.email.tracking_id})
        response = self.client.get(url)

        # Assert response status and type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/gif')

        # Assert no-cache headers
        self.assertEqual(response.headers['Cache-Control'], 'no-cache, no-store, must-revalidate, max-age=0')
        self.assertEqual(response.headers['Pragma'], 'no-cache')
        self.assertEqual(response.headers['Expires'], '0')

        # Assert event creation
        self.assertEqual(EmailOpenEvent.objects.filter(email=self.email).count(), 1)
        event = EmailOpenEvent.objects.filter(email=self.email).first()
        self.assertFalse(event.is_prefetch)

    def test_repeated_opens_tracked(self):
        """
        Verify that multiple requests to the tracking pixel create multiple open events.
        """
        url = reverse('track-email-open', kwargs={'tracking_id': self.email.tracking_id})

        # Send request 3 times
        for _ in range(3):
            self.client.get(url)

        # Assert 3 events created
        self.assertEqual(EmailOpenEvent.objects.filter(email=self.email).count(), 3)

    def test_alternate_tracking_url(self):
        """
        Verify that the alternate path /track/open/<tracking_id>/ also works correctly.
        """
        url = reverse('track-email-open-alternate', kwargs={'tracking_id': self.email.tracking_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/gif')
        self.assertEqual(EmailOpenEvent.objects.filter(email=self.email).count(), 1)

    def test_invalid_tracking_id_silent_failure(self):
        """
        Verify that an invalid tracking ID fails silently: returns 200 with pixel
        and does not raise exceptions or redirect.
        """
        random_id = uuid.uuid4()
        url = reverse('track-email-open', kwargs={'tracking_id': random_id})
        response = self.client.get(url)

        # Should still return 200 with GIF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/gif')
        # No events should be created
        self.assertEqual(EmailOpenEvent.objects.count(), 0)

    def test_prefetch_detection(self):
        """
        Verify that requests from prefetch clients / bots are marked as is_prefetch = True.
        """
        url = reverse('track-email-open', kwargs={'tracking_id': self.email.tracking_id})

        # Request 1: Prefetch header
        response = self.client.get(url, HTTP_PURPOSE='prefetch')
        self.assertEqual(response.status_code, 200)
        event1 = EmailOpenEvent.objects.order_by('-opened_at').first()
        self.assertTrue(event1.is_prefetch)

        # Request 2: Suspicious user agent pattern
        response = self.client.get(url, HTTP_USER_AGENT='Mozilla/5.0 GoogleImageProxy')
        self.assertEqual(response.status_code, 200)
        event2 = EmailOpenEvent.objects.order_by('-opened_at').first()
        self.assertTrue(event2.is_prefetch)
