import base64
from django.core.files.base import ContentFile


from .models import Customer, Order, Product, Store, User

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer


from phonenumber_field.serializerfields import PhoneNumberField
from taggit.serializers import TagListSerializerField, TaggitSerializer


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
            'first_name',
            'last_name',
            'avatar',
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


class StoreSerializer(serializers.Serializer):
    class Meta:
        model = Store
        fields = '__all__'
        
        def update(self, instance, validated_data):
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance


class StoreSearchSerializer(serializers.Serializer):
    pass


class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Product
        fields = [
            'id',
            'store',
            'title',
            'available',
            'discount',
            'description',
            'price',
            'image',
            'currency',
            'sale_price',
            'tags',
            'sales',
            'created',
            'updated'
        ]


class OrderSerializer(serializers.ModelSerializer):
    name = UserSerializer(related_name)
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            # 'name',
            'status',
            'cart',
            'total',
            'subtotal',
            'created',
            'updated'
        ]


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

    def validate_file(self, value):
        """
        Validate the uploaded file to ensure it is an MP3 file.
        """
        if not value.name.endswith('.mp3'):
            raise serializers.ValidationError('The uploaded file must be an MP3 file.')
        return value



class AdminSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=225)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=220, read_only=True)


class NotificationSerializer(serializers.Serializer):
    email_notification = serializers.BooleanField(default=False)
    sms_notification = serializers.BooleanField(default=False)
