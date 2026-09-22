from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

from .models import VerificationCode

User = get_user_model()

class EmailVerificationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.verify_url = reverse('verify-email')
        self.resend_url = reverse('resend-verification')
        
    def test_registration_creates_unverified_user_and_sends_email(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_verified)
        
        # Check that verification code was created
        self.assertEqual(VerificationCode.objects.filter(user=user).count(), 1)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Verify your BiteUp account', mail.outbox[0].subject)
        
    def test_unverified_user_cannot_login(self):
        # Create unverified user
        User.objects.create_user(username='test', email='unverified@example.com', password='password', is_verified=False)
        
        response = self.client.post(self.login_url, {
            'email': 'unverified@example.com',
            'password': 'password'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('not been verified', response.data['detail'])
        
    def test_successful_verification(self):
        user = User.objects.create_user(username='test2', email='verify@example.com', password='password', is_verified=False)
        
        code_str = '123456'
        VerificationCode.objects.create(
            user=user,
            purpose='EMAIL_VERIFICATION',
            code_hash=make_password(code_str),
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        response = self.client.post(self.verify_url, {
            'email': 'verify@example.com',
            'code': code_str
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        
        # Code should be deleted
        self.assertEqual(VerificationCode.objects.filter(user=user).count(), 0)
        
    def test_expired_code_is_rejected(self):
        user = User.objects.create_user(username='test3', email='expired@example.com', password='password', is_verified=False)
        
        code_str = '123456'
        VerificationCode.objects.create(
            user=user,
            purpose='EMAIL_VERIFICATION',
            code_hash=make_password(code_str),
            expires_at=timezone.now() - timedelta(minutes=1) # Expired
        )
        
        response = self.client.post(self.verify_url, {
            'email': 'expired@example.com',
            'code': code_str
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', response.data['detail'])
        user.refresh_from_db()
        self.assertFalse(user.is_verified)
        
    def test_resend_verification_cooldown(self):
        user = User.objects.create_user(username='test4', email='resend@example.com', password='password', is_verified=False)
        
        VerificationCode.objects.create(
            user=user,
            purpose='EMAIL_VERIFICATION',
            code_hash=make_password('111111'),
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        response = self.client.post(self.resend_url, {
            'email': 'resend@example.com'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please wait', response.data['detail'])
