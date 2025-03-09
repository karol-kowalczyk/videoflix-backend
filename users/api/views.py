from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail, get_connection
from django.conf import settings
from ..models import CustomUser, PasswordResetToken  # Importiere dein User- und Token-Modell
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer  # Serializer importieren
import uuid  # Für eindeutige Token
from django.utils import timezone
from django.urls import reverse
import smtplib
from email.mime.text import MIMEText
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

# SMTP-Einstellungen
SMTP_HOST = 'mail.karol-kowalczyk.de'
SMTP_PORT = 465
SMTP_USER = 'no-reply@videoflix.karol-kowalczyk.de'
SMTP_PASSWORD = 'no-reply.videoflix-1'
USE_SSL = True

# 🟢 Funktion zum Senden von E-Mails mit Link
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

# 🟢 Registrierung
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registrierung erfolgreich!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🟢 Login
class LoginView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        try:
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

# 🟢 E-Mail prüfen und Passwort-Reset-Link senden
class CheckEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                # 🟢 Token generieren und speichern
                token = str(uuid.uuid4())
                PasswordResetToken.objects.create(
                    user=user, 
                    token=token, 
                    expires_at=timezone.now() + timezone.timedelta(hours=1)
                )

                # 🟢 Link generieren für localhost mit kodierter Benutzer-ID
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://localhost:4200/set-new-password?uid={uidb64}&token={token}"
                send_test_email(email, reset_link)  # Link in die E-Mail packen

                return Response({"message": "E-Mail existiert. Link zum Zurücksetzen wurde gesendet."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"message": "E-Mail existiert nicht."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "E-Mail-Adresse fehlt!"}, status=status.HTTP_400_BAD_REQUEST)

# 🟢 Passwort zurücksetzen mit Token
User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            # 🟢 Debug: Zeige UID und Token
            print(f"UIDB64: {uidb64}, Token: {token}")

            # Benutzer-ID entschlüsseln
            uid = urlsafe_base64_decode(uidb64).decode()
            print(f"Entschlüsselte Benutzer-ID: {uid}")

            user = User.objects.get(pk=uid)

            # 🟢 Überprüfen, ob der Token in der DB existiert und gültig ist
            try:
                reset_token = PasswordResetToken.objects.get(user=user, token=token)
                
                # Prüfen, ob der Token abgelaufen ist
                if reset_token.expires_at < timezone.now():
                    print("Token ist abgelaufen!")
                    return Response({"error": "Ungültiger oder abgelaufener Token!"}, status=status.HTTP_400_BAD_REQUEST)
            
            except PasswordResetToken.DoesNotExist:
                print("Ungültiger Token!")
                return Response({"error": "Ungültiger oder abgelaufener Token!"}, status=status.HTTP_400_BAD_REQUEST)

            # 🟢 Neues Passwort setzen
            new_password = request.data.get('new_password')
            if new_password:
                user.password = make_password(new_password)
                user.save()
                # 🟢 Token löschen nach erfolgreicher Passwortänderung
                reset_token.delete()
                return Response({"message": "Passwort erfolgreich geändert!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Kein Passwort angegeben!"}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"Fehler: {e}")
            return Response({"error": "Ungültiger Benutzer!"}, status=status.HTTP_400_BAD_REQUEST)
