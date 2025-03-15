from .models import CustomUser
from django.core.mail import send_mail

def get_user_by_email(email):
    """
    Retrieve a user by their email address.

    Returns the user object if found, or None if not.
    """
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None

def send_reset_email(email):
    """
    Send a password reset email to the provided email address.

    Returns True if the email was sent successfully, otherwise False.
    """
    subject = 'Passwort zurücksetzen'
    message = 'Klicken Sie auf den Link, um Ihr Passwort zurückzusetzen.'
    from_email = 'test@example.com' 
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        return False