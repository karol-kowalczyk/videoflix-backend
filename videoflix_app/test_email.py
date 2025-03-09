import smtplib
from email.mime.text import MIMEText
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model

User = get_user_model()
SMTP_HOST = 'mail.karol-kowalczyk.de'
SMTP_PORT = 465
SMTP_USER = 'no-reply@videoflix.karol-kowalczyk.de'
SMTP_PASSWORD = 'no-reply.videoflix-1'
USE_SSL = True

token_generator = PasswordResetTokenGenerator()

def send_test_email(recipient):
    try:
        user = User.objects.get(email=recipient)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_link = f"http://localhost:4200/set-new-password?uid={uid}&token={token}"

        sender = 'no-reply@videoflix.karol-kowalczyk.de'
        subject = 'Passwort zurücksetzen - Videoflix'
        body = f"""Hallo,

Klicke auf den folgenden Link, um dein Passwort zurückzusetzen:
{reset_link}

Der Link ist 1 Stunde gültig.

Viele Grüße,
Dein Videoflix-Team
"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        print("E-Mail erfolgreich gesendet!")
        return True
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")
        return False
