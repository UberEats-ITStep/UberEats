from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from users.models import User

class EmailService:
    @staticmethod
    def send_password_reset_code(user: User, code: str) -> bool:
        subject = "Reset your BiteUp password"

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
        Here is your secure password reset code for BiteUp.
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
                        No. 002
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

              <!-- Large Logo Area -->
              <tr>
                <td style="padding: 60px 32px 40px 32px; text-align: center; border-bottom: 1px solid #E2E2DF;">
                  <h1 style="margin: 0 0 16px 0; font-family: 'Instrument Serif', 'Playfair Display', Georgia, serif; font-size: 64px; font-weight: 400; font-style: italic; line-height: 1; letter-spacing: -1.5px; color: #191918;">
                    <span style="color: #007BFF;">Bite</span><span style="color: #FF8C00;">Up</span>
                  </h1>
                  <p style="margin: 0; font-size: 20px; font-weight: 500; letter-spacing: -0.5px; color: #191918;">
                    Password Reset.
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
                    A request has been made to reset the password for your BiteUp account. To proceed, please use the secure code provided below. This ensures your account remains protected.
                  </p>
                  
                  <!-- Code Container (Print Style) -->
                  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 40px;">
                    <tr>
                      <td style="border: 1px solid #191918; padding: 3px;">
                        <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="border: 1px solid #191918;">
                          <tr>
                            <td align="center" style="padding: 32px 24px; background-color: #F6F6F2;">
                              <div style="font-family: 'SF Mono', 'Courier New', Courier, monospace; font-size: 48px; font-weight: 700; letter-spacing: 16px; color: #191918; margin-left: 16px;">
                                {code}
                              </div>
                            </td>
                          </tr>
                          <tr>
                            <td align="center" style="padding: 12px; border-top: 1px solid #191918; background-color: #FFFFFF;">
                              <p style="margin: 0; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #191918;">
                                Valid for {getattr(settings, 'PASSWORD_RESET_CODE_TTL_SECONDS', 600) // 60} Minutes
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
        
        plain_message = f"""BiteUp - Password Reset

Here is your secure password reset code for BiteUp:
{code}

Valid for {getattr(settings, 'PASSWORD_RESET_CODE_TTL_SECONDS', 600) // 60} Minutes.

If you did not initiate this request, no further action is required and you may safely disregard this message.
"""

        return send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        ) == 1
