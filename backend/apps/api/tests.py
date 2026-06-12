import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.emails.models import Email
from apps.tracking.models import EmailOpenEvent

User = get_user_model()


class LiveStatsAPITestCase(TestCase):

    def setUp(self):
        self.client = Client()
        
        # Create user 1 and an email
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.email1 = Email.objects.create(
            sender=self.user1,
            recipient_email='recipient1@example.com',
            subject='Email 1 Subject',
            body='Hello World 1',
            status='SENT'
        )
        # Create an open event for email 1
        self.event1 = EmailOpenEvent.objects.create(
            email=self.email1,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 Test UA 1',
            is_prefetch=False
        )

        # Create user 2 and an email
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password456'
        )
        self.email2 = Email.objects.create(
            sender=self.user2,
            recipient_email='recipient2@example.com',
            subject='Email 2 Subject',
            body='Hello World 2',
            status='SENT'
        )

    def test_dashboard_stats_requires_authentication(self):
        """
        Verify that dashboard stats endpoint blocks unauthenticated requests with 401.
        """
        url = reverse('api-dashboard-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        
        # Verify JSON error message
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Authentication required.')

    def test_dashboard_stats_success(self):
        """
        Verify that an authenticated user can fetch their dashboard stats correctly.
        """
        self.client.login(username='user1', password='password123')
        url = reverse('api-dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Assert structure and values
        self.assertEqual(data['total_emails'], 1)
        self.assertEqual(data['sent_emails'], 1)
        self.assertEqual(data['opened_emails'], 1)
        self.assertEqual(data['total_open_events'], 1)
        self.assertIsNotNone(data['latest_open_time'])
        self.assertEqual(data['latest_open_time']['time'], self.event1.opened_at.strftime('%H:%M:%S'))
        
        # Assert lists
        self.assertEqual(len(data['recent_emails']), 1)
        self.assertEqual(data['recent_emails'][0]['id'], self.email1.id)
        self.assertEqual(data['recent_emails'][0]['open_count'], 1)
        
        self.assertEqual(len(data['recent_events']), 1)
        self.assertEqual(data['recent_events'][0]['id'], self.event1.id)
        self.assertEqual(data['recent_events'][0]['ip_address'], '192.168.1.1')
        
        # No repeated opens yet
        self.assertEqual(len(data['repeated_emails']), 0)

    def test_email_stats_requires_authentication(self):
        """
        Verify that email stats endpoint blocks unauthenticated requests with 401.
        """
        url = reverse('api-email-stats', kwargs={'pk': self.email1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_email_stats_success(self):
        """
        Verify that an authenticated owner can fetch details for their email.
        """
        self.client.login(username='user1', password='password123')
        url = reverse('api-email-stats', kwargs={'pk': self.email1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['email_id'], self.email1.id)
        self.assertEqual(data['open_count'], 1)
        self.assertEqual(data['unique_opens_count'], 1)
        self.assertEqual(len(data['events']), 1)
        self.assertEqual(data['events'][0]['id'], self.event1.id)
        self.assertEqual(data['events'][0]['ip_address'], '192.168.1.1')
        self.assertEqual(data['events'][0]['user_agent'], 'Mozilla/5.0 Test UA 1')
        self.assertFalse(data['events'][0]['is_prefetch'])

    def test_email_stats_forbidden_for_non_owner(self):
        """
        Verify that a user cannot access another user's email stats (returns 403).
        """
        # Log in as user2, but request email1 (owned by user1)
        self.client.login(username='user2', password='password456')
        url = reverse('api-email-stats', kwargs={'pk': self.email1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Permission denied.')

    def test_email_stats_not_found(self):
        """
        Verify that requesting non-existent email ID returns 404.
        """
        self.client.login(username='user1', password='password123')
        url = reverse('api-email-stats', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
