from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    ROLE_CHOICES = (
        ('CLIENT', 'CLIENT'),
        ('COURIER', 'COURIER'),
        ('ADMIN', 'ADMIN'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    # Require email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class VerificationCode(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password reset'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_codes',
    )
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purpose', 'created_at']),
        ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} Profile"

from django.utils import timezone

class VerificationCode(models.Model):
    PURPOSE_CHOICES = (
        ('EMAIL_VERIFICATION', 'Email Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='EMAIL_VERIFICATION')
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
        return timezone.now() <= self.expires_at

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
