from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail, get_connection
from django.conf import settings
from ..models import CustomUser, PasswordResetToken, ActivationToken
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
import uuid
from django.utils import timezone
from django.urls import reverse
import smtplib
from datetime import timedelta
from email.mime.text import MIMEText
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from decouple import config
from django.contrib.auth.hashers import make_password

SMTP_HOST = 'mail.karol-kowalczyk.de'
SMTP_PORT = 465
SMTP_USER = 'no-reply@videoflix.karol-kowalczyk.de'
SMTP_PASSWORD = config('SMTP_PASSWORD')
use_ssl = True

def create_message(recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'no-reply@videoflix.karol-kowalczyk.de'
    msg['To'] = recipient
    return msg

def send_email(recipient, subject, body):
    msg = create_message(recipient, subject, body)
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print(f"{subject} E-Mail gesendet!")
            return True
    except Exception as e:
        print(f"Fehler beim Senden der {subject} E-Mail: {e}")
        return False

def send_test_email(recipient, reset_link):
    subject = 'Passwort zurücksetzen - Videoflix'
    body = f"Hallo,\n\nKlicken Sie auf den folgenden Link, um Ihr Passwort zurückzusetzen:\n{reset_link}\n\nDer Link ist 1 Stunde gültig.\n\nViele Grüße,\nDein Videoflix-Team"
    return send_email(recipient, subject, body)

def send_activation_email(recipient, activation_link):
    subject = 'Account aktivieren - Videoflix'
    body = f"Hallo,\n\nklicken Sie auf den folgenden Link, um Ihren Account zu aktivieren:\n{activation_link}\n\nDer Link ist 24 Std gültig.\n\nViele Grüße,\nDein Videoflix-Team"
    return send_email(recipient, subject, body)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(days=1)
            activation_token = ActivationToken.objects.create(user=user, token=token, expires_at=expires_at)
            activation_link = f"https://videoflix-backend.karol-kowalczyk.de/activate-account?token={token}"
            send_activation_email(user.email, activation_link)
            return Response({"message": "Registrierung erfolgreich!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    def activate_user(self, user):
        user.is_activated = True
        user.save()

    def post(self, request):
        token = request.data.get('token')
        if token:
            try:
                activation_token = ActivationToken.objects.get(token=token)
                if activation_token.is_valid():
                    self.activate_user(activation_token.user)
                    activation_token.delete()
                    return Response({"message": "Account aktiviert."}, status=status.HTTP_200_OK)
                return Response({"error": "Aktivierungslink ist abgelaufen."}, status=status.HTTP_400_BAD_REQUEST)
            except ActivationToken.DoesNotExist:
                return Response({"error": "Ungültiger Aktivierungstoken."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response({"message": "Ungültige Anmeldedaten."}, status=status.HTTP_401_UNAUTHORIZED)

class CheckEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            return self.handle_valid_email(email)
        return Response({"error": "E-Mail-Adresse fehlt!"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_valid_email(self, email):
        try:
            user = CustomUser.objects.get(email=email)
            token = self.generate_reset_token(user)
            uidb64 = self.encode_user_id(user)
            reset_link = self.create_reset_link(uidb64, token)
            self.send_reset_email(email, reset_link)
            return Response({"message": "E-Mail existiert. Link zum Zurücksetzen wurde gesendet."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "E-Mail existiert nicht."}, status=status.HTTP_404_NOT_FOUND)

    def generate_reset_token(self, user):
        token = str(uuid.uuid4())
        PasswordResetToken.objects.create(user=user, token=token, expires_at=timezone.now() + timedelta(hours=1))
        return token

    def encode_user_id(self, user):
        return urlsafe_base64_encode(force_bytes(user.pk))

    def create_reset_link(self, uidb64, token):
        return f"https://videoflix-backend.karol-kowalczyk.de/set-new-password?uid={uidb64}&token={token}"

    def send_reset_email(self, email, reset_link):
        send_test_email(email, reset_link)

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({"detail": "Neues Passwort fehlt."}, status=status.HTTP_400_BAD_REQUEST)
            user = self.get_user_from_uid(uidb64)
            self.validate_token(user, token)
            user.password = make_password(new_password)
            user.save()
            return Response({"detail": "Passwort erfolgreich zurückgesetzt."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": "Ungültiger Link oder abgelaufener Token."}, status=status.HTTP_400_BAD_REQUEST)

    def get_user_from_uid(self, uidb64):
        uid = urlsafe_base64_decode(uidb64).decode()
        return get_user_model().objects.get(pk=uid)

    def validate_token(self, user, token):
        reset_token = PasswordResetToken.objects.get(user=user, token=token)
        if not reset_token.is_valid():
            raise ValueError("Ungültiger oder abgelaufener Token.")