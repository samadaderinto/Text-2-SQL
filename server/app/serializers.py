from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import Order, Product, User

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status

from phonenumber_field.serializerfields import PhoneNumberField
from taggit.serializers import TagListSerializerField, TaggitSerializer



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
    

class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "title",
            "available",
            "discount",
            "description",
            "price",
            "sale_price",
            "tags",
            "sales",
            "created",
            "updated"
        ]
        

class OrderSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "cart",
            "total",
            "subtotal",
            "created",
            "updated"
        ]
        
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
        

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=90, write_only=True)
    token = serializers.CharField(min_length=6, max_length=90, write_only=True)
    uidb64 = serializers.CharField(min_length=6, max_length=90, write_only=True)

    fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", status.HTTP_401_UNAUTHORIZED)
            user.set_password(password)
            user.save()
        except:
            raise AuthenticationFailed("The reset link is invalid", status.HTTP_401_UNAUTHORIZED)
        return super().validate(attrs)