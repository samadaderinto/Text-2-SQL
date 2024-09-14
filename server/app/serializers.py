from .models import Customer, Order, Product, Store, User

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from phonenumber_field.serializerfields import PhoneNumberField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'created', 'updated']
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            user.make_password(self.password)
            user.save()
            return user


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'created',
            'updated'
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()


class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD


class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['user', 'username', 'email', 'name', 'bio', 'phone', 'currency']


class ProductSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'store',
            'title',
            'available',
            'description',
            'price',
            # 'image',
            'category',
            'currency',
            'sales',
            'created',
            'updated'
        ]
        extra_kwargs = {'sales': {'read_only': True}}

    # def get_image(self, obj):
    #     request = self.context.get('request')
    #     if obj.image and request:
    #         return request.build_absolute_uri(obj.image.url)
    #     return None


class OrderSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'name',
            'status',
            'cart',
            'total',
            'subtotal',
            'created',
            'updated'
        ]

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
    password = serializers.CharField(max_length=220, read_only=True)


class NotificationSerializer(serializers.Serializer):
    email_notification = serializers.BooleanField(default=False)
    sms_notification = serializers.BooleanField(default=False)


class SearchSerializer(serializers.Serializer):
    search = serializers.CharField()
