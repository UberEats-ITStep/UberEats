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
      <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Instrument+Serif:ital@0;1&display=swap');
      </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F6F6F2; color: #191918; -webkit-font-smoothing: antialiased;">
      <!-- Hidden Preheader Text -->
      <div style="display: none; max-height: 0px; overflow: hidden; mso-hide: all; font-size: 0px; line-height: 0px; color: #F6F6F2;">
        Here is your secure verification code for BiteUp.
        &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
      </div>
      <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #F6F6F2; padding: 40px 10px;">
        <tr>
          <td align="center">
            <!-- Main Card -->
            <table role="presentation" width="100%" max-width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%; background-color: #FFFFFF; border: 1px solid #E2E2DF;">
              
              <!-- Editorial Top Bar -->
              <tr>
                <td style="padding: 16px 32px; border-bottom: 1px solid #191918;">
                  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                      <td align="left" style="font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #191918;">
                        Authentication
                      </td>
                      <td align="right" style="font-size: 10px; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; color: #5F5F5C;">
                        No. 001
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Large Logo Area -->
              <tr>
                <td style="padding: 60px 32px 40px 32px; text-align: center; border-bottom: 1px solid #E2E2DF;">
                  <h1 style="margin: 0 0 16px 0; font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif; font-size: 64px; font-weight: 400; font-style: italic; line-height: 1; letter-spacing: -1.5px; color: #191918;">
                    BiteUp
                  </h1>
                  <p style="margin: 0; font-size: 20px; font-weight: 500; letter-spacing: -0.5px; color: #191918;">
                    Account Verification.
                  </p>
                </td>
              </tr>
              
              <!-- Content Body -->
              <tr>
                <td style="padding: 40px 32px;">
                  <p style="margin: 0 0 24px 0; font-size: 16px; line-height: 26px; color: #191918; font-weight: 500;">
                    Hello {user.username},
                  </p>
                  
                  <p style="margin: 0 0 40px 0; font-size: 16px; line-height: 26px; color: #5F5F5C;">
                    A request has been made to verify your email address. To proceed, please use the secure code provided below. This ensures your account remains protected.
                  </p>
                  
                  <!-- Code Container (Print Style) -->
                  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 40px;">
                    <tr>
                      <td style="border: 1px solid #191918; padding: 3px;">
                        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="border: 1px solid #191918;">
                          <tr>
                            <td align="center" style="padding: 32px 24px; background-color: #F6F6F2;">
                              <div style="font-family: 'SF Mono', 'Courier New', Courier, monospace; font-size: 48px; font-weight: 700; letter-spacing: 16px; color: #191918; margin-left: 16px;">
                                {plaintext_code}
                              </div>
                            </td>
                          </tr>
                          <tr>
                            <td align="center" style="padding: 12px; border-top: 1px solid #191918; background-color: #FFFFFF;">
                              <p style="margin: 0; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #191918;">
                                Valid for {getattr(settings, 'EMAIL_VERIFICATION_CODE_EXPIRATION_MINUTES', 15)} Minutes
                              </p>
                            </td>
                          </tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                  
                  <p style="margin: 0; font-size: 14px; line-height: 22px; color: #5F5F5C;">
                    If you did not initiate this request, no further action is required and you may safely disregard this message.
                  </p>
                </td>
              </tr>
              
            </table>
            
            <!-- Footer -->
            <table role="presentation" width="100%" max-width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%; margin-top: 24px;">
              <tr>
                <td align="center" style="padding: 0 32px;">
                  <p style="margin: 0 0 8px 0; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #191918;">
                    BiteUp Technologies
                  </p>
                  <p style="margin: 0; font-size: 11px; color: #8E8E8B;">
                    &copy; {timezone.now().year} All rights reserved. Do not reply to this automated email.
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

    plain_message = f"""BiteUp - Account Verification

Here is your secure verification code for BiteUp:
{plaintext_code}

Valid for {getattr(settings, 'EMAIL_VERIFICATION_CODE_EXPIRATION_MINUTES', 15)} Minutes.

If you did not initiate this request, no further action is required and you may safely disregard this message.
"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Failed to send verification email via SMTP")
        raise ValueError("Could not send verification email. Please check your email configuration.")


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
