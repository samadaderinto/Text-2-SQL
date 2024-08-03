from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action


from .serializers import LoginSerializer, ResetPasswordSerializer, UserSerializer
from .services import AuthService, CustomerService, OrderService, ProductService, QueryService, SettingsService


from drf_spectacular.utils import extend_schema
from kink import di
# Create your views here.




class AuthViewSet(viewsets.GenericViewSet):
    
    auth_service: AuthService = di[AuthService]
    
    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.login(
            request,
            serializer.validated_data["phone"],
            serializer.validated_data["password"]
        )
        return Response(status=status.HTTP_200_OK, data=result["data"], headers=result["token"])
    
    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["post"])
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.create_user(
            serializer.validated_data["name"],
            serializer.validated_data["phone"],
            serializer.validated_data["email"],
            serializer.validated_data["password"],
            request,
        )
        return Response(status=201, data=result["data"], headers=result["token"])
    
    
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
    
    
class QueryViewSet(viewsets.GenericViewSet):
    query_service: QueryService = di[QueryService]
    
    
    def audio_to_text(self, request):
        pass
    
    def text_to_SQL(self, request):
        pass
    
    def runSQLQuery(self, request):
        pass

    
    

class ProductViewSet(viewsets.GenericViewSet):
    product_service: ProductService = di[ProductService]


class CustomerViewSet(viewsets.GenericViewSet):
    customer_service: CustomerService = di[CustomerService]


class OrderViewSet(viewsets.GenericViewSet):
    order_service: OrderService = di[OrderService]
    
    
class SettingsViewSet(viewsets.GenericViewSet):
    settings_service: SettingsService = di[SettingsService]