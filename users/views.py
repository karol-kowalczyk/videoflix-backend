from django.shortcuts import render
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import CustomUser

class RequestPasswordResetView(APIView):
    """
    API view to handle password reset requests. 
    It checks if the user exists and sends a reset email if the email is valid.
    """

    def post(self, request):
        """
        Handle POST request to initiate password reset process.

        The email address is retrieved from the request. If the email is valid and associated with
        an existing user, an email with a password reset link is sent.
        """
        email = request.data.get('email')
        if not email:
            return self.invalid_email_response()  # Respond if email is not provided

        user = self.get_user_by_email(email)
        if not user:
            return self.user_not_found_response()  # Respond if no user found with the provided email

        if self.send_reset_email(email):
            return Response({"message": "E-Mail gesendet."}, status=status.HTTP_200_OK)  # Respond on success
        else:
            return self.email_send_error_response()  # Respond if email sending fails

    def invalid_email_response(self):
        """
        Return a response indicating that the email address is required.
        """
        return Response({"message": "E-Mail-Adresse erforderlich"}, status=status.HTTP_400_BAD_REQUEST)

    def user_not_found_response(self):
        """
        Return a response indicating that no user was found with the given email address.
        """
        return Response({"message": "Kein Benutzer mit dieser E-Mail-Adresse gefunden"}, status=status.HTTP_404_NOT_FOUND)

    def get_user_by_email(self, email):
        """
        Retrieve a user by their email address.

        Returns the user object if found, or None if not.
        """
        try:
            return CustomUser.objects.get(email=email)  # Attempt to fetch the user by email
        except CustomUser.DoesNotExist:
            return None  # Return None if no user is found

    def send_reset_email(self, email):
        """
        Send a password reset email to the provided email address.

        The email includes a message instructing the user to reset their password.
        Returns True if the email was sent successfully, otherwise False.
        """
        subject = 'Passwort zurücksetzen'
        message = 'Klicken Sie auf den Link, um Ihr Passwort zurückzusetzen.'
        from_email = 'test@example.com'  # Sender's email address
        recipient_list = [email]  # Recipient email address list

        try:
            send_mail(subject, message, from_email, recipient_list)  # Send the email
            return True  # Return True if email is sent successfully
        except Exception as e:
            return False  # Return False if an error occurs while sending the email

    def email_send_error_response(self):
        """
        Return a response indicating that an error occurred while sending the email.
        """
        return Response({"message": "Fehler beim Senden der E-Mail."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
