from .models import Customer, Notification, NotificationDevice, Order, Product, Store, User

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name", "created", "updated"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value, user=self.instance)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "created",
            "updated",
        ]
        extra_kwargs = {"user": {"read_only": True}}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value


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


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["user", "username", "email", "name", "bio", "phone", "currency"]
        extra_kwargs = {"user": {"read_only": True}}


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "title",
            "available",
            "description",
            "price",
            "category",
            "currency",
            "sales",
            "created",
            "updated",
        ]
        extra_kwargs = {"sales": {"read_only": True}, "store": {"read_only": True}}


class OrderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "name",
            "status",
            "cart",
            "total",
            "subtotal",
            "created",
            "updated",
        ]
        extra_kwargs = {"user": {"read_only": True}}

    def get_name(self, obj):
        return obj.user.first_name


class OrderSearchSerializer(serializers.Serializer):
    id = serializers.CharField()
    user_id = serializers.CharField()


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomerSearchSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = PhoneNumberField()


class FileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class AdminSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=225)
    email = serializers.EmailField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["push_notification"]


class NotificationDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDevice
        fields = ["id", "token", "platform", "is_active", "created", "updated"]
        read_only_fields = ["id", "is_active", "created", "updated"]


class SearchSerializer(serializers.Serializer):
    search = serializers.CharField()


class QueryPlanSerializer(serializers.Serializer):
    prompt = serializers.CharField()
