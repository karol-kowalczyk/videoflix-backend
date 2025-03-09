from django.shortcuts import render
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import CustomUser


class RequestPasswordResetView(APIView):

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return self.invalid_email_response()

        user = self.get_user_by_email(email)
        if not user:
            return self.user_not_found_response()

        if self.send_reset_email(email):
            return Response({"message": "E-Mail gesendet."}, status=status.HTTP_200_OK)
        else:
            return self.email_send_error_response()

    def invalid_email_response(self):
        return Response({"message": "E-Mail-Adresse erforderlich"}, status=status.HTTP_400_BAD_REQUEST)

    def user_not_found_response(self):
        return Response({"message": "Kein Benutzer mit dieser E-Mail-Adresse gefunden"}, status=status.HTTP_404_NOT_FOUND)

    def get_user_by_email(self, email):
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None

    def send_reset_email(self, email):
        subject = 'Passwort zurücksetzen'
        message = 'Klicken Sie auf den Link, um Ihr Passwort zurückzusetzen.'
        from_email = 'test@example.com'
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            return False

    def email_send_error_response(self):
        return Response({"message": "Fehler beim Senden der E-Mail."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
