import os

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.core.files.storage import default_storage

from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny

from .models import Customer, Order, Product, User
from .permissions import ServerAccessPolicy
from .serializers import CustomerSerializer, CustomerSearchSerializer,  EmailSerializer, LogOutSerializer, LoginSerializer, OrderSerializer, ProductSerializer, ResetPasswordSerializer, OrderSearchSerializer, UserSerializer, FileSerializer
from .services import AuthService, CustomerService, OrderService, ProductService, QueryService, SettingsService

from rest_access_policy import AccessViewSetMixin
from drf_spectacular.utils import extend_schema
from kink import di

from utils.algorithms import TokenGenerator, auth_token, send_email, send_mail

from rest_framework_simplejwt.tokens import RefreshToken

from pydub import AudioSegment
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")
class AuthViewSet(viewsets.GenericViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service: AuthService = di[AuthService] 
        self.User = User
        
    
    # permission_classes = (AllowAny,)

    permission_classes = (ServerAccessPolicy,)
    serializer_class = UserSerializer
    
    
    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["post"], url_path="signup")
   
    def signup(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.create_user(request,serializer.validated_data["email"],serializer.validated_data["password"])
        
        if result:
            return Response({'message': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User successfully created, Verify your email account'},status=status.HTTP_201_CREATED)
    
    
    @extend_schema(responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['get'], url_path='activate/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)', name="activate")
    def verify_activation(self, request, uidb64, token):
       
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(self.User, pk=id)
            
            if user.is_active:
                return Response({'message': 'Account is already activated'}, status=status.HTTP_200_OK)

            if not TokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user.is_active = True
            user.save()
            
            # relative_link = f'self.auth_service.get_base_url(request)/auth/login/'
            # abs_link = request.build_absolute_uri(relative_link)
        
            return redirect('http://localhost:8000/auth/login/', permanent=True)
      
    
    @extend_schema(request=LogOutSerializer, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        data = JSONParser().parse(request)
        serializer = LogOutSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data['refresh']).blacklist()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={"Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        
    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        data = self.auth_service.login_user(request,serializer.validated_data["email"],serializer.validated_data["password"])
        
        if data.get("token", None) and data.get("data", None):
             return Response(status=status.HTTP_200_OK, data=data["data"], headers=data["token"])
        elif data.get("verify", None):
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": data["verify"]})
        elif data.get("invalid_info", None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Invalid user information"})
          
        
    # @extend_schema(request=LoginSerializer, responses={status.HTTP_200_OK: UserSerializer})
    # @action(detail=False, methods=['post'], url_path='login/refresh')
    # def login_token_refresh(self):
    #     return TokenRefreshView.as_view()
    
    @extend_schema(request=EmailSerializer, responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=['post'], url_path='reset-password/request')
    def request_reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = EmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        absolute_url = self.auth_service.request_reset_password_user(request, email)
        send_email(absolute_url)
        return Response({'success': 'We have sent you a mail to reset your password'}, status=status.HTTP_200_OK)
        
        
    
    @extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['get'], url_path='reset-password/verify/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def verify_password_reset_token(self, request, uidb64, token):
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

        return redirect('http://localhost:8000/auth/reset-password/reset/', permanent=True)
    
    
    @extend_schema(request=ResetPasswordSerializer, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=["post"], url_path="reset-password/reset")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]
        message = self.auth_service.reset_password_user(request, email, new_password)
        return Response(data=message, status=status.HTTP_205_RESET_CONTENT)


    
    
class QueryViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_service: QueryService = di[QueryService]
        
        
    permission_classes = (ServerAccessPolicy,)
    parser_classes = [MultiPartParser, FormParser]
  
    
    
    @extend_schema(request=FileSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['post'], url_path='upload')
    def audio_to_query(self, request):
        serializer = FileSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        audio_file = serializer.validated_data['file']
        file_path = default_storage.save('temp_audio_file', audio_file)

        try:
                audio = AudioSegment.from_file(file_path)
                wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
                audio.export(wav_file_path, format='wav')
                result = self.query_service.runSQLQuery(request, wav_file_path, file_path)
        finally:
                os.remove(file_path)
                os.remove(wav_file_path)
        return Response(result, status=status.HTTP_200_OK)

    
class ProductViewSet(viewsets.GenericViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service: ProductService = di[ProductService]
        
        
    # pagination_class = Paginator
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    
    
    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def create_product(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = self.product_service.create_product(request.user, **serializer.validated_data) 
        return Response(status=201, data=ProductSerializer(product).data)
    
    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def update_product(self, request,  pk=None):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.product_service.update_product(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=ProductSerializer(product).data)
    
    
    @extend_schema(responses={200: ProductSerializer})
    def retrieve_product(self, request):
        product = self.get_object()
        serializer = ProductSerializer(product)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def delete_product(self, request):
        self.product_service.delete_product(request.user)
        return Response(status=204)


class CustomerViewSet(viewsets.GenericViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_service: CustomerService = di[CustomerService]
        
        
    # pagination_class = Paginator
    permission_classes = (ServerAccessPolicy,)
  

    
    @extend_schema(request=CustomerSerializer, responses={200: CustomerSerializer})
    @action(detail=False, methods=['post'], url_path='create')
    def create_customer(self, request):
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        customer = self.customer_service.create_customer(request, serializer) 
        return Response(status=201, data=customer)
    
    @extend_schema(request=CustomerSerializer, responses={200: CustomerSerializer})
    @action(detail=False, methods=['put'], url_path='update')
    def update_customer(self, request):
        data = JSONParser().parse(request)
        customer = self.customer_service.update_customer(data)
        return Response(status=201, data=customer)
    
    @extend_schema(responses={200: CustomerSerializer})
    @action(detail=False, methods=['get'], url_path='get')
    def retrieve_customer(self, request, pk=None):
        data = JSONParser().parse(request)
        serializer = CustomerSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        phone_number = serializer.validated_data["phone_number"]
        customer = self.customer_service.get_customer(request, email= email, phone_number=phone_number)
        
        return Response(status=200, data=customer)

    @extend_schema(responses={204: None})
    @action(detail=False, methods=['post'], url_path='ban')
    def ban(self, request):
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(data=data)
        user = self.customer_service.ban_customer(request.user)
        


class OrderViewSet(viewsets.GenericViewSet):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service: OrderService = di[OrderService]
        
        
    # pagination_class = Paginator
    permission_classes = (AllowAny,)
    serializer_class = OrderSerializer

    
    @extend_schema(request=OrderSerializer, responses={200: OrderSerializer})
    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request):
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = self.order_service.create_order(request, serializer) 
        return Response(status=201, data=order)

    
    @extend_schema(request=OrderSerializer, responses={200: OrderSerializer})
    @action(detail=False, methods=['put'], url_path='update')
    def update_order(self, request):
        data = JSONParser().parse(request)
        customer = self.order_service.update_order(data)
        return Response(status=201, data=customer)
    
    @extend_schema(responses={200: UserSerializer})
    @action(detail=False, methods=['get'], url_path='get')
    def retrieve_order(self, request):
    
        data = JSONParser().parse(request)
        serializer = OrderSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data["id"]
        user_id = serializer.validated_data["user_id"]
        customer = self.order_service.get_order(request, id= id, user_id=user_id)
        
        return Response(status=200, data=customer)
    
    
class SettingsViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_service: SettingsService = di[SettingsService]
        
    
    permission_classes = (ServerAccessPolicy,)
    
    