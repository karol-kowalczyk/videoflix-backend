from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and validating a new user.

    This serializer handles user registration, validating passwords, and ensuring that 
    the password and confirm_password fields match.
    """
    
    confirm_password = serializers.CharField(write_only=True, required=True)  # Field for confirming password

    class Meta:
        model = User 
        fields = ['id', 'email', 'password', 'confirm_password'] 
        extra_kwargs = {
            'password': {'write_only': True}, 
        }

    def validate(self, attrs):
        """
        Validate that the 'password' and 'confirm_password' fields match.
        Also validates the password strength using Django's built-in password validation.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        validate_password(attrs['password']) 
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance.

        The confirm_password field is not saved. The user's password is hashed and saved securely.
        """
        validated_data.pop('confirm_password') 
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username', validated_data['email'])
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT token pairs (access and refresh tokens).

    This serializer overrides the default serializer to use the 'email' field as the unique identifier
    and checks whether the user's account is activated.
    """
    
    username_field = 'email'

    def validate(self, attrs):
        """
        Validate the user credentials and check if the account is activated.
        
        If the user is not activated, an exception is raised.
        """
        data = super().validate(attrs)
        user = self.user 
        if not user.is_activated:
            raise exceptions.AuthenticationFailed('Account not activated.')
        data.update({
            'token': data.pop('access'), 
            'user': {
                "id": self.user.id,
                "email": self.user.email
            }
        })
        return data
