from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        # Entferne confirm_password bevor der User erstellt wird
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            # Automatisch generierter Username als Fallback
            username=validated_data.get('username', validated_data['email'])
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Email als Login-Feld verwenden
    username_field = 'email'

    def validate(self, attrs):
        # Konvertiere email zu lowercase
        attrs['email'] = attrs.get('email', '').lower()
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['user_id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'token': data.pop('access'),
            'user': {
                'id': self.user.id,
                'email': self.user.email
            }
        })
        return data