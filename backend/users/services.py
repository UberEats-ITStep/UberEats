import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import strip_tags

from .models import VerificationCode


def generate_verification_code(user, purpose="EMAIL_VERIFICATION"):
    # Check cooldown (60 seconds)
    recent_code = VerificationCode.objects.filter(
        user=user,
        purpose=purpose,
        created_at__gte=timezone.now() - timedelta(seconds=60),
    ).first()

    if recent_code:
        raise ValueError("Please wait before requesting another verification code.")

    # Delete previous unused codes for this purpose
    VerificationCode.objects.filter(user=user, purpose=purpose).delete()

    # Generate cryptographically secure 6-digit code
    plaintext_code = str(secrets.randbelow(1000000)).zfill(6)

    # Store hashed version
    expiration_minutes = getattr(
        settings, "EMAIL_VERIFICATION_CODE_EXPIRATION_MINUTES", 15
    )

    VerificationCode.objects.create(
        user=user,
        purpose=purpose,
        code_hash=make_password(plaintext_code),
        expires_at=timezone.now() + timedelta(minutes=expiration_minutes),
    )

    return plaintext_code


def send_verification_email(user, plaintext_code):
    subject = "Verify your BiteUp account"

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, Arial, sans-serif; background-color: #F1F5F9; color: #0F1633;">
      <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F1F5F9; padding: 60px 20px;">
        <tr>
          <td align="center">
            <!-- Main Card -->
            <table role="presentation" width="100%" max-width="600px" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(15, 22, 51, 0.1), 0 8px 10px -6px rgba(15, 22, 51, 0.05); border: 1px solid #E2E8F0; margin: 0 auto;">
              
              <!-- Header Gradient Background -->
              <tr>
                <td style="background: linear-gradient(135deg, #0F1633 0%, #1B2447 100%); padding: 40px; text-align: center;">
                  <h1 style="margin: 0; font-family: 'Outfit', 'Inter', Arial, sans-serif; font-size: 36px; font-weight: 800; letter-spacing: -0.5px;">
                    <span style="color: #3B82F6;">Bite</span><span style="color: #FF8C00;">Up</span>
                  </h1>
                </td>
              </tr>
              
              <!-- Body -->
              <tr>
                <td style="padding: 48px 40px;">
                  <h2 style="margin-top: 0; margin-bottom: 24px; color: #0F1633; font-family: 'Outfit', 'Inter', Arial, sans-serif; font-size: 24px; font-weight: 700; text-align: center;">Verify your email address</h2>
                  
                  <p style="margin: 0 0 16px 0; font-size: 16px; line-height: 26px; color: #475569; text-align: center;">
                    Hi {user.username},
                  </p>
                  
                  <p style="margin: 0 0 40px 0; font-size: 16px; line-height: 26px; color: #475569; text-align: center;">
                    Welcome to BiteUp! You are just one step away from discovering the best local restaurants around you. Please enter the verification code below to complete your registration.
                  </p>
                  
                  <!-- Code Box -->
                  <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); border: 2px dashed #CBD5E1; border-radius: 12px; padding: 32px 24px; text-align: center; margin-bottom: 40px;">
                    <span style="font-family: 'Courier New', Courier, monospace; font-size: 42px; font-weight: 800; letter-spacing: 12px; color: #0F1633;">{plaintext_code}</span>
                  </div>
                  
                  <p style="margin: 0 0 16px 0; font-size: 14px; line-height: 22px; color: #64748B; text-align: center;">
                    This code will expire securely in <strong>{getattr(settings, 'EMAIL_VERIFICATION_CODE_EXPIRATION_MINUTES', 15)} minutes</strong>.
                  </p>
                  
                  <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 40px 0 32px 0;" />
                  
                  <p style="margin: 0; font-size: 13px; line-height: 20px; color: #94A3B8; text-align: center;">
                    If you didn't request this email, you can safely ignore it. Your account will not be created until verified.
                  </p>
                </td>
              </tr>
            </table>
            
            <!-- Footer -->
            <table role="presentation" width="100%" max-width="600px" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 32px auto 0 auto;">
              <tr>
                <td align="center" style="padding: 0 24px;">
                  <p style="margin: 0; font-size: 13px; color: #94A3B8; font-family: 'Inter', Arial, sans-serif;">
                    &copy; {timezone.now().year} BiteUp Technologies Inc. All rights reserved.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def verify_user_code(user, plaintext_code, purpose="EMAIL_VERIFICATION"):
    if user.is_verified and purpose == "EMAIL_VERIFICATION":
        raise ValueError("Email already verified.")

    # Clean up expired codes globally when accessed
    VerificationCode.objects.filter(expires_at__lt=timezone.now()).delete()

    active_codes = VerificationCode.objects.filter(user=user, purpose=purpose)

    if not active_codes.exists():
        raise ValueError("Verification code is invalid or has expired.")

    code_record = active_codes.latest("created_at")

    if not code_record.is_valid():
        raise ValueError("Verification code has expired.")

    if not check_password(plaintext_code, code_record.code_hash):
        raise ValueError("Verification code is invalid.")

    # Verification successful
    if purpose == "EMAIL_VERIFICATION":
        user.is_verified = True
        user.save(update_fields=["is_verified"])

    # Strictly single-use: delete all verification codes for this user/purpose
    VerificationCode.objects.filter(user=user, purpose=purpose).delete()
    return True
