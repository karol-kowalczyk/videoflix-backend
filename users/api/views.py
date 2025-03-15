"""
Authentication and user management views.

This module contains API views for user registration, account activation, login, 
password reset, and email verification in the Videoflix application.
"""

import uuid
import smtplib
import os
import subprocess
from datetime import timedelta
from email.mime.text import MIMEText

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail, get_connection
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.shortcuts import render
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CustomUser, PasswordResetToken, ActivationToken
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from decouple import config

# SMTP configuration for email sending
SMTP_HOST = 'mail.karol-kowalczyk.de'
SMTP_PORT = 465
SMTP_USER = 'no-reply@videoflix.karol-kowalczyk.de'
SMTP_PASSWORD = config('SMTP_PASSWORD')
USE_SSL = True

def create_message(recipient, subject, body):
    """
    Creates an email message using MIMEText.

    Args:
        recipient (str): Recipient email address.
        subject (str): Subject of the email.
        body (str): Email content.

    Returns:
        MIMEText: The constructed email message.
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = recipient
    return msg

def send_email(recipient, subject, body):
    """
    Sends an email using an SMTP server.

    Args:
        recipient (str): Recipient email address.
        subject (str): Subject of the email.
        body (str): Email content.

    Returns:
        bool: True if the email is sent successfully, False otherwise.
    """
    msg = create_message(recipient, subject, body)
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print(f"{subject} Email sent successfully!")
            return True
    except Exception as e:
        print(f"Error sending {subject} email: {e}")
        return False

def send_activation_email(recipient, activation_link):
    """
    Sends an account activation email.

    Args:
        recipient (str): Recipient email address.
        activation_link (str): Activation link URL.
    """
    subject = 'Activate Account - Videoflix'
    body = f"Hello,\n\nClick the following link to activate your account:\n{activation_link}\n\nThe link is valid for 24 hours.\n\nBest regards,\nYour Videoflix Team"
    send_email(recipient, subject, body)

class RegisterView(APIView):
    """
    API endpoint for user registration.
    """
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(days=1)
            ActivationToken.objects.create(user=user, token=token, expires_at=expires_at)
            activation_link = f"https://videoflix.karol-kowalczyk.de/activate-account?token={token}"
            send_activation_email(user.email, activation_link)
            return Response({"message": "Registration successful! Please check your email to activate your account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    """
    API endpoint for activating a user account via an activation token.
    """
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
                    return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
                return Response({"error": "Activation link has expired."}, status=status.HTTP_400_BAD_REQUEST)
            except ActivationToken.DoesNotExist:
                return Response({"error": "Invalid activation token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Token is missing."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API endpoint for user login.
    """
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response({"message": "Invalid login credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class CheckEmailView(APIView):
    """
    API endpoint to check if an email exists in the system and send a password reset link.
    """
    def post(self, request):
        email = request.data.get('email')
        if email:
            return self.handle_valid_email(email)
        return Response({"error": "Email address is missing!"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_valid_email(self, email):
        try:
            user = CustomUser.objects.get(email=email)
            token = self.generate_reset_token(user)
            uidb64 = self.encode_user_id(user)
            reset_link = self.create_reset_link(uidb64, token)
            send_email(email, "Reset Password - Videoflix", f"Click here to reset your password: {reset_link}")
            return Response({"message": "Email exists. Reset link has been sent."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "Email does not exist."}, status=status.HTTP_404_NOT_FOUND)

    def generate_reset_token(self, user):
        token = str(uuid.uuid4())
        PasswordResetToken.objects.create(user=user, token=token, expires_at=timezone.now() + timedelta(hours=1))
        return token

    def encode_user_id(self, user):
        return urlsafe_base64_encode(force_bytes(user.pk))

    def create_reset_link(self, uidb64, token):
        return f"https://videoflix.karol-kowalczyk.de/set-new-password?uid={uidb64}&token={token}"

class ResetPasswordView(APIView):
    """
    API endpoint for resetting a user's password.
    """
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({"detail": "New password is missing."}, status=status.HTTP_400_BAD_REQUEST)
            user = self.get_user_from_uid(uidb64)
            self.validate_token(user, token)
            user.password = make_password(new_password)
            user.save()
            return Response({"detail": "Password successfully reset."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Invalid link or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    def get_user_from_uid(self, uidb64):
        uid = urlsafe_base64_decode(uidb64).decode()
        return get_user_model().objects.get(pk=uid)

    def validate_token(self, user, token): 
        reset_token = PasswordResetToken.objects.get(user=user, token=token)
        if not reset_token.is_valid():
            raise ValueError("Invalid or expired token.")
