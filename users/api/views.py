from datetime import timedelta
import uuid
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CustomUser, ActivationToken
from ..serializers import UserSerializer, CustomTokenObtainPairSerializer
from .utils import (
    send_activation_email,
    generate_reset_token,
    encode_user_id,
    create_reset_link,
    send_email,
    get_user_from_uid,
    validate_token,
    activate_user,

)


class RegisterView(APIView):
    """
    API endpoint for user registration.
    Handles POST requests to create a new user and send an activation email.
    """

    def post(self, request):
        """
        Process the registration request.
        
        - Validates the input data using UserSerializer.
        - Creates a new user if the data is valid.
        - Generates an activation token and sends an activation email.
        - Returns a success message or error details.
        
        Args:
            request: The HTTP request object containing user registration data.
        
        Returns:
            Response: A success message with HTTP 201 status or error details with HTTP 400 status.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(days=1) 
            ActivationToken.objects.create(user=user, token=token, expires_at=expires_at)
            activation_link = f"http://localhost:4200/activate-account?token={token}"
            send_activation_email(user.email, activation_link)
            return Response(
                {"message": "Registration successful! Please check your email to activate your account."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    """
    API endpoint for activating a user account via an activation token.
    Handles POST requests to activate the account based on the provided token.
    """

    def post(self, request):
        """
        Process the activation request.
        
        - Retrieves the token from the request data.
        - Checks if the token is valid and not expired.
        - Activates the user account if the token is valid.
        - Deletes the activation token after successful activation.
        - Returns a success message or error details.
        
        Args:
            request: The HTTP request object containing the activation token .
        
        Returns:
            Response: A success message with HTTP 200 status or error details with HTTP 400 status.
        """
        token = request.data.get('token')
        if token:
            try:
                activation_token = ActivationToken.objects.get(token=token)
                if activation_token.is_valid():
                    activate_user(activation_token.user)
                    activation_token.delete()
                    return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
                return Response({"error": "Activation link has expired."}, status=status.HTTP_400_BAD_REQUEST)
            except ActivationToken.DoesNotExist:
                return Response({"error": "Invalid activation token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Token is missing."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.
    Handles POST requests to authenticate the user and return a token.
    """

    def post(self, request):
        """
        Process the login request.
        
        - Validates the login credentials using CustomTokenObtainPairSerializer.
        - Returns the token if credentials are valid, otherwise returns an error message.
        
        Args:
            request: The HTTP request object containing login credentials.
        
        Returns:
            Response: Token data with HTTP 200 status or error message with HTTP 401 status.
        """
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response({"message": "Invalid login credentials."}, status=status.HTTP_401_UNAUTHORIZED)


class CheckEmailView(APIView):
    """
    API endpoint to check if an email exists and send a password reset link.
    Handles POST requests to verify the email and initiate the password reset process.
    """

    def post(self, request):
        """
        Process the email check request.
        
        - Retrieves the email from the request data.
        - Calls handle_valid_email if the email is provided.
        - Returns an error if the email is missing.
        
        Args:
            request: The HTTP request object containing the email.
        
        Returns:
            Response: Result from handle_valid_email or error with HTTP 400 status.
        """
        email = request.data.get('email')
        if email:
            return self.handle_valid_email(email)
        return Response({"error": "Email address is missing!"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_valid_email(self, email):
        """
        Handle the logic for a valid email.
        
        - Checks if the email exists in the database.
        - Generates a reset token and sends a reset email if the email exists.
        - Returns a success message or an error if the email does not exist.
        
        Args:
            email (str): The email address to check.
        
        Returns:
            Response: Success message with HTTP 200 status or error with HTTP 404 status.
        """
        try:
            user = CustomUser.objects.get(email=email)
            token = generate_reset_token(user)
            uidb64 = encode_user_id(user)
            reset_link = create_reset_link(uidb64, token)
            send_email(email, "Reset Password - Videoflix", f"Click here to reset your password: {reset_link}")
            return Response({"message": "Email exists. Reset link has been sent."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": "Email does not exist."}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    """
    API endpoint for resetting a user's password.
    Handles POST requests to reset the password using the provided token and UID.
    """

    def post(self, request, uidb64, token, *args, **kwargs):
        """
        Process the password reset request.
        
        - Retrieves the new password from the request data.
        - Validates the token and UID.
        - Resets the password if the token is valid.
        - Returns a success message or error details.
        
        Args:
            request: The HTTP request object containing the new password.
            uidb64 (str): The base64-encoded user ID.
            token (str): The password reset token.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        
        Returns:
            Response: Success message with HTTP 200 status or error details with HTTP 400 status.
        """
        try:
            new_password = request.data.get('new_password')
            if not new_password:
                return Response({"detail": "New password is missing."}, status=status.HTTP_400_BAD_REQUEST)
            user = get_user_from_uid(uidb64)
            validate_token(user, token)
            user.password = make_password(new_password)
            user.save()
            return Response({"detail": "Password successfully reset."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Invalid link or expired token."}, status=status.HTTP_400_BAD_REQUEST)