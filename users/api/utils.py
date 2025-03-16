import os
import uuid
import smtplib
from email.mime.text import MIMEText
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from ..models import ActivationToken, PasswordResetToken
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart



def create_message(recipient, subject, body):
    """
    Creates an email message with MIMEText.

    This function creates an email message with the specified recipient, subject, and content.
    It sets the 'From', 'To', and 'Subject' headers with the provided details and the SMTP_USER from settings.

    Args:
        recipient (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email content.

    Returns:
        MIMEText: The created email message.
    """
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_USER
    msg['To'] = recipient
    return msg


def send_email(recipient, subject, body):
    """
    Sends an email via an SMTP server.

    This function creates an email message using create_message and attempts to send it through an SMTP server 
    configured in Django settings. It manages the connection, authentication, and sending of the email.

    Args:
        recipient (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email content.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    msg = create_message(recipient, subject, body)
    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print(f"{subject} email sent successfully!")
            return True
    except Exception as e:
        print(f"Error sending {subject} email: {e}")
        return False

def send_activation_email(recipient, activation_link):
    """
    Sends an account activation email with a styled HTML body.
    The email includes inline CSS for improved visual design.
    """
    subject = 'Activate Your Account - Videoflix'
    body = f"""
    <html>
      <head>
        <style type="text/css">
          body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
          }}
          .container {{
            max-width: 600px;
            margin: auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
          }}
          h2 {{
            color: #white;
            backgrund-color: #4856E3;
          }}
          .btn {{
            display: inline-block;
            background-color: #4856E3;
            color: #fff;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 20px;
            margin-top: 20px;
          }}
          p {{
            line-height: 1.5;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h2>Activate Your Account</h2>
          <p>Hello,</p>
          <p>Click the following link to activate your account:</p>
          <p><a class="btn" href="{activation_link}">Activate Account</a></p>
          <p>The link is valid for 24 hours.</p>
          <p>Best regards,<br>Your Videoflix Team</p>
        </div>
      </body>
    </html>
    """
    send_email(recipient, subject, body)


def generate_reset_token(user):
    """
    Generates a reset token for password reset.

    This function creates a unique password reset token, sets an expiration time of 1 hour,
    and stores it in the PasswordResetToken model.

    Args:
        user: The user instance for which the token is generated.

    Returns:
        str: The generated reset token.
    """
    token = str(uuid.uuid4())
    expires_at = timezone.now() + timedelta(hours=1) 
    PasswordResetToken.objects.create(user=user, token=token, expires_at=expires_at)
    return token


def encode_user_id(user):
    """
    Encodes the user ID for URL safety.

    This function encodes the user's primary key using base64 to safely use it in URLs.

    Args:
        user: The user instance whose ID should be encoded.

    Returns:
        str: The base64-encoded user ID.
    """
    return urlsafe_base64_encode(force_bytes(user.pk))


def create_reset_link(uidb64, token):
    """
    Creates a password reset link.

    This function generates a password reset URL using the encoded user ID and reset token.

    Args:
        uidb64 (str): The base64-encoded user ID.
        token (str): The reset token.

    Returns:
        str: The complete password reset URL.
    """
    return f"http://localhost:4200/set-new-password?uid={uidb64}&token={token}"


def get_user_from_uid(uidb64):
    """
    Retrieves a user based on an encoded UID.

    This function decodes the base64-encoded user ID and fetches the corresponding user from the database.

    Args:
        uidb64 (str): The base64-encoded user ID.

    Returns:
        User: The user instance corresponding to the decoded UID.
    """
    uid = urlsafe_base64_decode(uidb64).decode()
    return get_user_model().objects.get(pk=uid)


def validate_token(user, token):
    """
    Validates a password reset token.

    This function checks whether the provided token is valid and has not expired for the given user.
    If the token is invalid or expired, a ValueError is raised.

    Args:
        user: The user instance associated with the token.
        token (str): The reset token to validate.

    Raises:
        ValueError: If the token is invalid or expired.
    """
    reset_token = PasswordResetToken.objects.get(user=user, token=token)
    if not reset_token.is_valid():
        raise ValueError("Invalid or expired token.")


def activate_user(user):
    """
    Activates a user account.

    This function sets the 'is_activated' field of the user to True and saves the changes.

    Args:
        user: The user instance to activate.
    """
    user.is_activated = True
    user.save()
