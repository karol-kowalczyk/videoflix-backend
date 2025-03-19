from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .utils import get_user_by_email, send_reset_email
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
            return self.invalid_email_response()

        user = get_user_by_email(email)
        if not user:
            return self.user_not_found_response()

        if send_reset_email(email):
            return Response({"message": "Email sent."}, status=status.HTTP_200_OK)
        else:
            return self.email_send_error_response()

    def invalid_email_response(self):
        """
        Return a response indicating that the email address is required.
        """
        return Response({"message": "Email address required."}, status=status.HTTP_400_BAD_REQUEST)

    def user_not_found_response(self):
        """
        Return a response indicating that no user was found with the given email address.
        """
        return Response({"message": "No user found with this email address."}, status=status.HTTP_404_NOT_FOUND)

    def email_send_error_response(self):
        """
        Return a response indicating that an error occurred while sending the email.
        """
        return Response({"message": "Error occurred while sending the email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
