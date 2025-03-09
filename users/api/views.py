from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail, get_connection
from django.conf import settings
from ..models import CustomUser, PasswordResetToken
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
import uuid
from django.utils import timezone
from django.urls import reverse
import smtplib
from email.mime.text import MIMEText
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from decouple import config

SMTP_HOST = 'mail.karol-kowalczyk.de'
SMTP_PORT = 465
SMTP_USER = 'no-reply@videoflix.karol-kowalczyk.de'
SMTP_PASSWORD = config('SMTP_PASSWORD')
USE_SSL = True

def send_test_email(recipient, reset_link):
    sender = 'no-reply@videoflix.karol-kowalczyk.de'
    subject = 'Passwort zurücksetzen - Videoflix'
    body = f"Hallo,\n\nKlicke auf den folgenden Link, um dein Passwort zurückzusetzen:\n{reset_link}\n\nDer Link ist 1 Stunde gültig.\n\nViele Grüße,\nDein Videoflix-Team"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        print("E-Mail erfolgreich gesendet!")
        return True
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")
        return False

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registrierung erfolgreich!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        try:
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

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
        PasswordResetToken.objects.create(
            user=user, 
            token=token, 
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )
        return token

    def encode_user_id(self, user):
        return urlsafe_base64_encode(force_bytes(user.pk))

    def create_reset_link(self, uidb64, token):
        return f"http://localhost:4200/set-new-password?uid={uidb64}&token={token}"

    def send_reset_email(self, email, reset_link):
        send_test_email(email, reset_link)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            user = self.get_user_from_uid(uidb64)
            reset_token = self.get_reset_token(user, token)

            if self.is_token_expired(reset_token):
                return Response({"error": "Ungültiger oder abgelaufener Token!"}, status=status.HTTP_400_BAD_REQUEST)

            return self.reset_password(request, user, reset_token)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"Fehler: {e}")
            return Response({"error": "Ungültiger Benutzer!"}, status=status.HTTP_400_BAD_REQUEST)

    def get_user_from_uid(self, uidb64):
        uid = urlsafe_base64_decode(uidb64).decode()
        return User.objects.get(pk=uid)

    def get_reset_token(self, user, token):
        return PasswordResetToken.objects.get(user=user, token=token)

    def is_token_expired(self, reset_token):
        return reset_token.expires_at < timezone.now()

    def reset_password(self, request, user, reset_token):
        new_password = request.data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
            user.save()
            reset_token.delete()
            return Response({"message": "Passwort erfolgreich geändert!"}, status=status.HTTP_200_OK)
        return Response({"error": "Kein Passwort angegeben!"}, status=status.HTTP_400_BAD_REQUEST)
