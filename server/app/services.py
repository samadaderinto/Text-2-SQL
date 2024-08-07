from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from django.utils.encoding import smart_str, force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from typing import Type
from kink import inject
from openai import OpenAI

from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action

from utils.algorithms import TokenGenerator, auth_token, send_mail

from .serializers import EmailSerializer, LoginSerializer, OrderSerializer, ProductSerializer, ResetPasswordSerializer, SetNewPasswordSerializer, UserSerializer
from .models import Product, User

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

@inject
class AuthService:
    def __init__(
        self,
        User: Type[User]):
        
        self.User = User
        self.Product = Product
        
    
    
    def send_activation_mail(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uuidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = TokenGenerator().make_token(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse('activate', kwargs={'uidb64': uuidb64, 'token': token})
        absolute_url = f"http://{current_site}{relativeLink}"
        send_mail("onboarding-user", user.email, data={"firstname": user.first_name, "absolute_url": absolute_url})
        
        
    @extend_schema(responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=['get'], url_path='activate')
    def verify_activation(self, request, uidb64, token):
        
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not TokenGenerator().check_token(user, token):
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
        user.is_active = True
        user.save()
        
        return Response({'message': 'Email verified, you can now login'}, status=status.HTTP_200_OK)
    
        
    @extend_schema(request=UserSerializer, responses={status.HTTP_201_CREATED: UserSerializer})
    @action(detail=False, methods=['post'], url_path='register')
    def create_user(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        if self.User.objects.filter(email=email).exists():
            return Response({'message': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        self.User.objects.create_user(**data)
        self.send_activation_mail(request, email)
        return Response({"message": "User successfully created, Verify your email account"}, status=status.HTTP_201_CREATED)

    @extend_schema(request=LoginSerializer, responses={status.HTTP_200_OK: UserSerializer})
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(self.User, email = data['email'])
        token = auth_token(user)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, headers={"Authorization": token}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @extend_schema(request=LoginSerializer, responses={status.HTTP_200_OK: UserSerializer})
    @action(detail=False, methods=['post'], url_path='login/refresh')
    def login_token_refresh(self):
        return TokenRefreshView.as_view()
    
   
    @extend_schema(request=None, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        data = JSONParser().parse(request)
        try:
            RefreshToken(data['refresh']).blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    @extend_schema(request=EmailSerializer, responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=['post'], url_path='reset-password/request')
    def request_reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = EmailSerializer(email = data['email'])
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(self.User, email = data['email'])
        uidb64 = urlsafe_base64_encode(user.id.to_bytes())
        token = PasswordResetTokenGenerator().make_token(user)
        
        current_site = get_current_site(request).domain
        relativeLink = reverse('password_reset_confirmation', kwargs={'uidb64': uidb64, 'token': token})
        abs_url = f"http://{current_site}{relativeLink}"
        mail_data = {'absolute_url': abs_url, 'email': email}

        send_mail('password-reset', email, data=mail_data)

        return Response({'success': 'We have sent you a mail to reset your password'}, status=status.HTTP_200_OK)
        
    
    
    @extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['post'], url_path='reset-password/verify')
    def verify_password_reset_token(self, request, uidb64, token):
        
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        
        
    @extend_schema(request=SetNewPasswordSerializer, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=['post'], url_path='reset-password/')
    def reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = SetNewPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    
    
    
client = OpenAI(
    # default max_retries is 2
    max_retries=3,
    api_key=settings.OPENAI_API_KEY
)
@inject
class QueryService:
    def __init__(
        self,
        User: Type[User]):
    
        pass
    
    def audio_to_text(self, request):
        pass
    
    def text_to_SQL(self, request):
        self.audio_to_text(request)
    
    def runSQLQuery(self, request):
        self.text_to_SQL(request)
    

@inject
class ProductService:
    def __init__(
        self,
        User: Type[User],
        Product: Type[Product]
    ):
        self.User = User
        self.Product = Product
    
    
    def get_products(self, product_id):
        product = get_object_or_404(self.Product, id=product_id)
        serializer = ProductSerializer(product)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def delete_product(self, product_id):
        product = get_object_or_404(self.Product, id=product_id)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)
    
    def create_product(self):
        pass
    
    def update_product(self):
        pass
        
    
    
        
  

@inject
class CustomerService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass
  
    def get_customers(self):
        pass
    
    def get_customer(self):
        pass 
    
    def ban_customer(self):
        pass
    
    def create_product(self):
        pass
    
    def update_product(self):
        pass
  
  
@inject
class OrderService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass
    
    def create_product(self):
        pass
    
    def update_product(self):
        pass
    
    def get_customers(self):
        pass
    
    def get_customer(self):
        pass
  
  
@inject
class SettingsService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass