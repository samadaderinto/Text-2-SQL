import os

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.files.storage import default_storage

from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action


from .models import Order, Product, User
from .permissions import ServerAccessPolicy
from .serializers import EmailSerializer, LoginSerializer, OrderSerializer, ProductSerializer, ResetPasswordSerializer, UserSerializer, SetNewPasswordSerializer, FileSerializer
from .services import AuthService, CustomerService, OrderService, ProductService, QueryService, SettingsService


from drf_spectacular.utils import extend_schema
from kink import di

from utils.algorithms import TokenGenerator, auth_token, send_mail

from rest_framework_simplejwt.tokens import RefreshToken

from openai import Audio
from pydub import AudioSegment



class AuthViewSet(viewsets.GenericViewSet):
    
    auth_service: AuthService = di[AuthService]
    
    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.login(
            request,
            serializer.validated_data["email"],
            serializer.validated_data["password"])
        return Response(status=status.HTTP_200_OK, data=result["data"], headers=result["token"])
    
    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.create_user(
            request,
            serializer.validated_data["first_name"],
            serializer.validated_data["last_name"],
            serializer.validated_data["avatar"],
            serializer.validated_data["phone"],
            serializer.validated_data["email"],
            serializer.validated_data["password"],
            
        )
        
        if result:
            return Response({'message': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User successfully created, Verify your email account'},status=status.HTTP_201_CREATED)
    
    
    @extend_schema(request=None, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        data = JSONParser().parse(request)
        
        try:
            RefreshToken(data['refresh']).blacklist()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_205_RESET_CONTENT)
    
    
    
    @extend_schema(responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=['get'], url_path='activate')
    def verify_activation(self, request, uidb64, token):
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not TokenGenerator().check_token(user, token):
            return Response(
                {'error': 'Token is not valid, please request a new one'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        user.is_active = True
        user.save()

        return Response({'message': 'Email verified, you can now login'}, status=status.HTTP_200_OK)
        
    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    @action(detail=False, methods=["post"], url_path="password/reset")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.reset_password(
            serializer.validated_data["code"],
            serializer.validated_data["phone"],
            serializer.validated_data["new_password"],
            request,
        )
        return Response(200, data=result["data"], headers=result["token"])
    
    @extend_schema(request=LoginSerializer, responses={status.HTTP_200_OK: UserSerializer})
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(self.User, email=data['email'])
        token = auth_token(user)
        user_serializer = UserSerializer(user)
        return Response(
            user_serializer.data,
            headers={'Authorization': token},
            status=status.HTTP_400_BAD_REQUEST)
        
    
    @extend_schema(request=LoginSerializer, responses={status.HTTP_200_OK: UserSerializer})
    @action(detail=False, methods=['post'], url_path='login/refresh')
    def login_token_refresh(self):
        return TokenRefreshView.as_view()
    
    
    @extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['post'], url_path='reset-password/verify')
    def verify_password_reset_token(self, request, uidb64, token):
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

    @extend_schema(request=EmailSerializer, responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=['post'], url_path='reset-password/request')
    def request_reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = EmailSerializer(email=data['email'])
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_object_or_404(self.User, email=data['email'])
        uidb64 = urlsafe_base64_encode(user.id.to_bytes())
        token = PasswordResetTokenGenerator().make_token(user)

        current_site = get_current_site(request).domain
        relativeLink = reverse(
            'password_reset_confirmation', kwargs={'uidb64': uidb64, 'token': token}
        )
        abs_url = f"http://{current_site}{relativeLink}"
        mail_data = {'absolute_url': abs_url, 'email': email}

        send_mail('password-reset', email, data=mail_data)

        return Response(
            {'success': 'We have sent you a mail to reset your password'},
            status=status.HTTP_200_OK
        )

    @extend_schema(request=SetNewPasswordSerializer, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=['post'], url_path='reset-password/')
    def reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = SetNewPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    
    
class QueryViewSet(viewsets.GenericViewSet):
    query_service: QueryService = di[QueryService]
    
    
    @extend_schema(request=FileSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['post'], url_path='upload/')
    def audio_to_query(self, request):
        if request.FILES.get('audio_file'):
            audio_file = request.FILES['audio_file']
            file_path = default_storage.save('temp_audio_file', audio_file)

            audio = AudioSegment.from_file(file_path)
            wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_file_path, format='wav')
            
            return self.query_service.runSQLQuery(request, wav_file_path, file_path)
                
        return Response({'error': 'Invalid request'}, status=400)

    
class ProductViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin):
    
    
    product_service: ProductService = di[ProductService]
    pagination_class = Paginator
    permission_classes = (ServerAccessPolicy,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
    
    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def create(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = self.product_service.create_budget(request.user, **serializer.validated_data) 
        return Response(status=201, data=ProductSerializer(product).data)
    
    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    def update(self, request,  pk=None):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.product_service.update_budget(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=ProductSerializer(product).data)
    
    
    @extend_schema(responses={200: ProductSerializer})
    def retrieve(self, request, pk=None):
        product = self.get_object()
        serializer = ProductSerializer(product)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        self.product_service.delete_budget(request.user, pk)
        return Response(status=204)


class CustomerViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin):
    
    
    customer_service: CustomerService = di[CustomerService]
    pagination_class = Paginator
    permission_classes = (ServerAccessPolicy,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(user=self.request.user)
    
    @extend_schema(request=UserSerializer, responses={200: UserSerializer})
    def create(self, request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        budget = self.customer_service.customer_service(request.user, **serializer.validated_data) 
        return Response(status=201, data=UserSerializer(budget).data)
    
    @extend_schema(request=UserSerializer, responses={200: UserSerializer})
    def update(self, request,  pk=None):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = self.customer_service.customer_service(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=UserSerializer(budget).data)
    
    
    @extend_schema(responses={200: UserSerializer})
    def retrieve(self, request, pk=None):
        budget = self.get_object()
        serializer = UserSerializer(budget)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        self.customer_service.customer_service(request.user, pk)
        return Response(status=204)


class OrderViewSet(viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin):
    
    order_service: OrderService = di[OrderService]
    pagination_class = Paginator
    permission_classes = (ServerAccessPolicy,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @extend_schema(request=OrderSerializer, responses={200: UserSerializer})
    def create(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        budget = self.order_service.order_service(request.user, **serializer.validated_data) 
        return Response(status=201, data=UserSerializer(budget).data)
    
    @extend_schema(request=OrderSerializer, responses={200: OrderSerializer})
    def update(self, request,  pk=None):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = self.order_service.order_service(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=OrderSerializer(budget).data)
    
    
    @extend_schema(responses={200: UserSerializer})
    def retrieve(self, request, pk=None):
        budget = self.get_object()
        serializer = OrderSerializer(budget)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        self.order_service.order_service(request.user, pk)
        return Response(status=204)
    
    
class SettingsViewSet(viewsets.GenericViewSet):
    settings_service: SettingsService = di[SettingsService]
    
    