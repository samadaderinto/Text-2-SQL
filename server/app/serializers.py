from .models import User

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
            "created",
            "updated",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            user.make_password(self.password)
            user.save()
            return user

class LoginSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    password = serializers.CharField()
    
class PhoneSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    
class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField()
    phone = PhoneNumberField()
    new_password = serializers.CharField()

class VerifyOtpSerializer(serializers.Serializer):
    code = serializers.CharField()
    phone = PhoneNumberField()
    
class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD
    
class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data