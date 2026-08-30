from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


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
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Email Verification'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_codes',
    )
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=32, choices=Purpose.choices, default=Purpose.EMAIL_VERIFICATION)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purpose', 'created_at']),
        ]

    def is_valid(self):
        return timezone.now() <= self.expires_at


class Profile(models.Model):
    class Avatar(models.TextChoices):
        AVATAR_01 = 'avatar_01', 'Avatar 01'
        AVATAR_02 = 'avatar_02', 'Avatar 02'
        AVATAR_03 = 'avatar_03', 'Avatar 03'
        AVATAR_04 = 'avatar_04', 'Avatar 04'
        AVATAR_05 = 'avatar_05', 'Avatar 05'
        AVATAR_06 = 'avatar_06', 'Avatar 06'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.CharField(
        max_length=20,
        choices=Avatar.choices,
        default=Avatar.AVATAR_01,
    )

    def __str__(self):
        return f"{self.user.email} Profile"


class DeliveryAddress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_addresses',
    )
    label = models.CharField(max_length=100)
    formatted_address = models.CharField(max_length=500)
    street = models.CharField(max_length=255, blank=True, default='')
    building = models.CharField(max_length=20, blank=True, default='')
    apartment = models.CharField(max_length=20, blank=True, default='')
    entrance = models.CharField(max_length=20, blank=True, default='')
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    delivery_notes = models.TextField(max_length=500, blank=True, default='')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_delivery_address_per_user',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(latitude__isnull=True, longitude__isnull=True)
                    | models.Q(latitude__isnull=False, longitude__isnull=False)
                ),
                name='delivery_address_coordinates_together',
            ),
        ]

    def __str__(self):
        return f'{self.label}: {self.formatted_address}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
