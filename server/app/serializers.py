from .models import Customer, Notification, NotificationDevice, Order, Product, Store, User

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from phonenumber_field.serializerfields import PhoneNumberField
from drf_spectacular.utils import extend_schema_field


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

    @extend_schema_field(serializers.CharField())
    def get_name(self, obj) -> str:
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
        fields = ["email_notification", "push_notification"]


class NotificationDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDevice
        fields = ["id", "token", "platform", "is_active", "created", "updated"]
        read_only_fields = ["id", "is_active", "created", "updated"]


class SearchSerializer(serializers.Serializer):
    search = serializers.CharField()


class QueryPlanSerializer(serializers.Serializer):
    prompt = serializers.CharField(help_text="Natural language query prompt describing the requested data or operation")


class JobAcceptedResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField(help_text="Unique identifier of the queued background task")
    status = serializers.CharField(help_text="Current execution status of the job (e.g. pending, processing)")


class QueueJobStatusResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField(help_text="Unique identifier of the queued background task")
    kind = serializers.CharField(help_text="Job kind (e.g. query_audio, query_generate, orders_export, email_password_reset)")
    status = serializers.ChoiceField(
        choices=["pending", "processing", "succeeded", "failed"],
        help_text="Current execution state",
    )
    result = serializers.JSONField(required=False, allow_null=True, help_text="Job output payload when succeeded")
    error = serializers.CharField(required=False, allow_null=True, help_text="Error message if the job failed")


class ProductSearchResponseSerializer(serializers.Serializer):
    products = ProductSerializer(many=True, help_text="List of matching products")
    count = serializers.IntegerField(help_text="Total count of matching products")
    total_pages = serializers.IntegerField(help_text="Total number of pages available")
    current_page = serializers.IntegerField(help_text="Current 1-based page index")


class CustomerSearchResponseSerializer(serializers.Serializer):
    customers = CustomerSerializer(many=True, help_text="List of matching customer records")
    count = serializers.IntegerField(help_text="Total count of matching customers")
    total_pages = serializers.IntegerField(help_text="Total number of pages available")
    current_page = serializers.IntegerField(help_text="Current 1-based page index")


class OrderSearchResponseSerializer(serializers.Serializer):
    orders = OrderSerializer(many=True, help_text="List of matching orders")
    count = serializers.IntegerField(help_text="Total count of matching orders")
    total_pages = serializers.IntegerField(help_text="Total number of pages available")
    current_page = serializers.IntegerField(help_text="Current 1-based page index")


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token (1-day validity)")
    refresh = serializers.CharField(help_text="JWT refresh token (7-day validity)")


class LoginResponseSerializer(serializers.Serializer):
    token = TokenPairSerializer(help_text="Issued JWT authentication tokens")
    data = UserSerializer(help_text="Authenticated user profile details")


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="Fresh JWT access token")
    refresh = serializers.CharField(help_text="Current JWT refresh token")


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Informational or success status message")


class ErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Description of the error condition")


class MutationConfirmationResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["success", "error"], help_text="Result status of the mutation execution")
    message = serializers.CharField(required=False, help_text="Status or explanation message")
    data = serializers.JSONField(required=False, help_text="Affected or created records")
