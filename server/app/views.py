from django.core.paginator import Paginator

from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import action


from .models import Order, Product, User
from .permissions import ServerAccessPolicy
from .serializers import LoginSerializer, OrderSerializer, ProductSerializer, ResetPasswordSerializer, UserSerializer
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
            serializer.validated_data["password"])
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

    
    

class ProductViewSet(viewsets.GenericViewSet, 
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin):
    
    
    product_service: ProductService = di[ProductService]
    pagination_class = Paginator
    authentication_classes = [ServerAccessPolicy]
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
    authentication_classes = [ServerAccessPolicy]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(user=self.request.user)
    
    @extend_schema(request=UserSerializer, responses={200: UserSerializer})
    def create(self, request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        budget = self.customer_service.create_budget(request.user, **serializer.validated_data) 
        return Response(status=201, data=UserSerializer(budget).data)
    
    @extend_schema(request=UserSerializer, responses={200: UserSerializer})
    def update(self, request,  pk=None):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = self.customer_service.update_budget(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=UserSerializer(budget).data)
    
    
    @extend_schema(responses={200: UserSerializer})
    def retrieve(self, request, pk=None):
        budget = self.get_object()
        serializer = UserSerializer(budget)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        self.customer_service.delete_budget(request.user, pk)
        return Response(status=204)


class OrderViewSet(viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,):
    order_service: OrderService = di[OrderService]
    
    pagination_class = Paginator
    authentication_classes = [ServerAccessPolicy]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @extend_schema(request=OrderSerializer, responses={200: UserSerializer})
    def create(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        budget = self.order_service.create_budget(request.user, **serializer.validated_data) 
        return Response(status=201, data=UserSerializer(budget).data)
    
    @extend_schema(request=OrderSerializer, responses={200: OrderSerializer})
    def update(self, request,  pk=None):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        budget = self.order_service.update_budget(request.user, pk, **serializer.validated_data)
        return Response(status=201, data=OrderSerializer(budget).data)
    
    
    @extend_schema(responses={200: UserSerializer})
    def retrieve(self, request, pk=None):
        budget = self.get_object()
        serializer = OrderSerializer(budget)
        return Response(status=200, data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        self.order_service.delete_budget(request.user, pk)
        return Response(status=204)
    
    
class SettingsViewSet(viewsets.GenericViewSet):
    settings_service: SettingsService = di[SettingsService]
    
    