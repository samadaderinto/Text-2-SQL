import csv
from http.client import HTTPResponse
from io import StringIO
import os
import logging
import subprocess

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.db.models import Q


from django_filters.rest_framework import DjangoFilterBackend


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import action, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers


from .models import Customer, Order, Product, Store, User
from .permissions import ServerAccessPolicy
from .serializers import (
    AdminSerializer,
    CustomerSerializer,
    CustomerSearchSerializer,
    EmailSerializer,
    FileSerializer,
    LogOutSerializer,
    LoginSerializer,
    NotificationSerializer,
    OrderSerializer,
    ProductSerializer,
    ResetPasswordSerializer,
    OrderSearchSerializer,
    StoreSearchSerializer,
    StoreSerializer,
    UserSerializer
)
from .services import (
    AuthService,
    CustomerService,
    OrderService,
    ProductService,
    QueryService,
    SettingsService,
    StoreService
)

from pydub import AudioSegment
from pydub.utils import which
from rest_framework_simplejwt.tokens import RefreshToken
from rest_access_policy import AccessViewSetMixin
from drf_spectacular.utils import extend_schema
from kink import di


from utils.algorithms import TokenGenerator, auth_token, send_email, send_mail


logger = logging.getLogger(__name__)

AudioSegment.converter = which('ffmpeg')


class AuthViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service: AuthService = di[AuthService]
        self.User = User

    # permission_classes = (AllowAny,)

    permission_classes = (ServerAccessPolicy,)
    serializer_class = UserSerializer

    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.create_user(
            request,
            serializer.validated_data['email'],
            serializer.validated_data['password']
        )

        if result:
            return Response(
                {'message': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'message': 'User successfully created, Verify your email account'},
            status=status.HTTP_201_CREATED
        )

    @extend_schema(responses={301: None})
    @action(
        detail=False,
        methods=['get'],
        url_path='activate/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)',
        name='activate'
    )
    def verify_activation(self, request, uidb64, token):
        try:
            # Decode the user ID from the base64 string
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            # Fetch the user from the database
            user = get_object_or_404(self.User, pk=user_id)

            # Check if the user is already active
            if user.is_active:
                return Response(
                    {'message': 'Account is already activated'},
                    status=status.HTTP_200_OK
                )

            # Validate the token
            if not TokenGenerator().check_token(user, token):
                return Response(
                    {'error': 'Token is not valid, please request a new one'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Activate the user account
            user.is_active = True
            user.save()

            # Redirect to the frontend sign-in page
            return redirect('http://localhost:4173/auth/signin', permanent=True)

        except Exception as e:
            # Handle exceptions and return an appropriate response
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=LogOutSerializer, responses={status.HTTP_205_RESET_CONTENT: None}
    )
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        data = JSONParser().parse(request)
        serializer = LogOutSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data['refresh'])
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        refresh.blacklist()
        return Response(
            data={'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT
        )

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        data = self.auth_service.login_user(
            request,
            serializer.validated_data['email'],
            serializer.validated_data['password']
        )
        if data.get('verify'):
            return Response(status=403, data={'message': data['verify']})
        elif data.get('token') and data.get('data'):
            return Response(status=status.HTTP_200_OK, data=data)

        elif data.get('invalid_info', None):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': 'Invalid user information'}
            )

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
        send_mail(
            f'Click on link to reset password, {email}',
            f"This is the link to reset password. {absolute_url}",
            'adesamad1234@gmail.com',
            [email],
            fail_silently=False
        )
        return Response(
            {'success': 'We have sent you a mail to reset your password'},
            status=status.HTTP_200_OK
        )

    @extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @action(
        detail=False,
        methods=['get'],
        url_path='reset-password/verify/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)'
    )
    def verify_password_reset_token(self, request, uidb64, token):
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(self.User, pk=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {'error': 'Token is not valid, please request a new one'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return redirect(
            f'http://localhost:4173/auth/reset-password/{user.email}', permanent=True
        )

    @extend_schema(
        request=ResetPasswordSerializer, responses={status.HTTP_205_RESET_CONTENT: None}
    )
    @action(detail=False, methods=['post'], url_path='reset-password/reset')
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        message = self.auth_service.reset_password_user(request, email, new_password)
        return Response(data=message, status=status.HTTP_205_RESET_CONTENT)


class QueryViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_service: QueryService = di[QueryService]

    permission_classes = (AllowAny,)
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=FileSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=['post'], url_path='upload')
    def audio_to_query(self, request):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        audio_file = serializer.validated_data['file']
        file_path = default_storage.save('uploaded_audio.mp3', audio_file)
        wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'

        try:
            # Use FFmpeg to convert MP3 to WAV with error handling
            result = subprocess.run(
                [
                    'ffmpeg',
                    '-y',  # Overwrite output file if it exists
                    '-analyzeduration',
                    '100M',
                    '-probesize',
                    '100M',
                    '-i',
                    file_path,
                    '-acodec',
                    'pcm_s16le',
                    '-ar',
                    '44100',
                    '-ac',
                    '2',
                    wav_file_path
                ],
                capture_output=True,
                text=True,
                check=True
            )

            # If FFmpeg succeeds, process the WAV file
            with open(wav_file_path, 'rb') as wav_file:
                result = self.query_service.runSQLQuery(request, wav_file.read())

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg Error: {e.stderr}")
            return Response(
                {'detail': 'Error processing audio file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return Response(
                {'detail': 'Error processing file.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Safely remove files if they exist
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if wav_file_path and os.path.exists(wav_file_path):
                os.remove(wav_file_path)

        return Response(result, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.GenericViewSet):
    permission_classes = (ServerAccessPolicy,)
    serializer_class = ProductSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service: ProductService = di[ProductService]

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    @action(detail=False, methods=['post'], url_path='create')
    @parser_classes([MultiPartParser])
    def create_product(self, request):
        try:
            serializer = ProductSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product = self.product_service.create_product(serializer)
            return Response(status=201, data=product)
        except serializers.ValidationError as e:
            logger.error(f"Validation error: {e.detail}")
            return Response(status=400, data={'error': e.detail})

        except Exception as e:
            logger.error(f"error: {e}")
            return Response(status=400)

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    @action(detail=False, methods=['put'], url_path='update')
    def update_product(self, request, pk=None):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.product_service.update_product(
            request.user, **serializer.validated_data
        )
        return Response(status=201, data=ProductSerializer(product).data)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='search')
    def retrieve_product(self, request):
        query = request.GET.get('query', '')
        products = Product.objects.all()

        if query:
            products = products.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__icontains=query)
            )

        page_number = request.GET.get('offset', 1)
        per_page = request.GET.get('limit', 15)

        paginator = Paginator(products, per_page)
        try:
            paginator_products = paginator.get_page(page_number)
        except (EmptyPage, PageNotAnInteger):
            paginator_products = paginator.page(1)

        serializer = ProductSerializer(paginator_products, many=True)

        response_data = {
            'products': serializer.data,
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': paginator_products.number
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    @action(detail=False, methods=['delete'], url_path='delete/(?P<product_id>[^/.]+)')
    def delete_product(self, request, product_id):
        self.product_service.delete_product(product_id)
        return Response(status=204)


class CustomerViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_service: CustomerService = di[CustomerService]

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

    @extend_schema(responses={200: CustomerSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='search')
    def retrieve_customer(self, request, pk=None):
        query = request.GET.get('query', '')
        page_number = int(request.GET.get('offset', 1))
        per_page = int(request.GET.get('limit', 15))

        # Filter customers based on the query string
        customers = Customer.objects.all()
        if query:
            customers = customers.filter(
                Q(first_name__icontains=query)
                | Q(email__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(last_name__icontains=query)
                | Q(created__icontains=query)
            )

        # Paginate the results
        paginator = Paginator(customers, per_page)
        paginated_customers = paginator.get_page(page_number)

        # Serialize the paginated data
        serializer = CustomerSerializer(paginated_customers, many=True)
        return Response(
            {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': paginated_customers.number,
                'customers': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(responses={204: None})
    @action(detail=False, methods=['post'], url_path='ban')
    def ban(self, request):
        data = JSONParser().parse(request)
        serializer = CustomerSerializer(data=data)
        user = self.customer_service.ban_customer(request.user)


class StoreViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store_service: StoreService = di[StoreService]

    # permission_classes = (ServerAccessPolicy,)
    permission_classes = (AllowAny,)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=['post'], url_path='create')
    def create_store(self, request):
        data = JSONParser().parse(request)
        serializer = StoreSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        customer = self.store_service.create_store(request, **serializer.data)
        return Response(status=201, data=customer)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=['put'], url_path='update')
    def update_store(self, request):
        data = JSONParser().parse(request)
        store = self.store_service.update_store(data)
        return Response(status=201, data=store)

    @extend_schema(responses={200: StoreSerializer})
    @action(detail=False, methods=['get'], url_path='get')
    def retrieve_store(self, request):
        data = JSONParser().parse(request)
        serializer = StoreSearchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        phone_number = serializer.validated_data['phone_number']
        customer = self.store_service.get_customer(
            request, email=email, phone_number=phone_number
        )

        return Response(status=200, data=customer)


class OrderViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service: OrderService = di[OrderService]

    permission_classes = (ServerAccessPolicy,)
    serializer_class = OrderSerializer

    @extend_schema(request=OrderSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=['post'], url_path='create')
    def create_order(self, request):
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = self.order_service.create_order(request, serializer)
        return Response(status=201, data=order)

    @extend_schema(responses={205: None})
    @action(detail=False, methods=['delete'], url_path='delete/(?P<order_id>[^/.]+)')
    def delete_order(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response(status=205)

    @extend_schema(request=OrderSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=['put'], url_path='update')
    def update_order(self, request):
        data = JSONParser().parse(request)
        customer = self.order_service.update_order(data)
        return Response(status=201, data=customer)

    @extend_schema(responses={200: OrderSerializer(many=True)})
    @action(detail=False, methods=['get'], url_path='search')
    def retrieve_order(self, request):
        query = request.GET.get('query', '')
        status_filter = request.GET.get('status', '')
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 15))

        # Search across multiple fields using Q objects
        orders = Order.objects.all()

        if query:
            orders = orders.filter(Q(id__icontains=query) | Q(status__icontains=query))

        if status_filter:
            orders = orders.filter(status=status_filter)

        try:
            paginator = Paginator(orders, limit)
            paginated_orders = paginator.get_page((offset // limit) + 1)
        except ValueError:
            return Response(
                {'detail': 'Invalid page or limit parameter.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderSerializer(paginated_orders.object_list, many=True)
        return Response(
            {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': paginated_orders.number,
                'orders': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(responses={200: None})
    @action(detail=False, methods=['get'], url_path='download')
    def download_order(self, request):
        orders = Order.objects.all()

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Order ID', 'Customer Name', 'Status', 'Date & Time', 'Price'])

        for order in orders:
            writer.writerow(
                [
                    order.id,
                    order.user.first_name,
                    order.status,
                    order.created,
                    order.subtotal
                ]
            )

        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        return response

    @extend_schema(responses={200: None})
    @action(detail=False, methods=['get'], url_path='download/(?P<order_id>[^/.]+)')
    def download_order(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Order ID', 'Customer Name', 'Status', 'Date & Time', 'Price'])

        writer.writerow(
            [
                order.id,
                order.user.first_name,
                order.status,
                order.created,
                order.subtotal
            ]
        )

        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="order_{order.id}.csv"'
        return response


class SettingsViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_service: SettingsService = di[SettingsService]
        self.store_service: StoreService = di[StoreService]

    # permission_classes = (ServerAccessPolicy,)
    permission_classes = (AllowAny,)

    @extend_schema(responses={200: AdminSerializer})
    @action(detail=False, methods=['get'], url_path='admin/get')
    def get_admin(self, request):
        admin_info = self.settings_service.get_admin_info(request.user.email)
        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(request=UserSerializer, responses={201: AdminSerializer})
    @action(detail=False, methods=['put'], url_path='admin/update')
    def edit_admin_info(self, request):
        data = JSONParser().parse(request)

        admin_info = self.settings_service.edit_admin_info(request.user.email, data)

        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(responses={200: StoreSerializer})
    @action(detail=False, methods=['get'], url_path='store/get')
    def get_store(self, request):
        store = get_object_or_404(Store, email=request.user.email)

        return Response(status=200, data=StoreSerializer(store).data)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=['put'], url_path='store/update')
    def update_store(self, request):
        data = JSONParser().parse(request)
        store = self.store_service.partially_update_store(request, data)
        return Response(status=201, data=store)

    @extend_schema(responses={200: NotificationSerializer})
    @action(detail=False, methods=['get'], url_path='notifications/get')
    def get_notification_info(self, request):
        notification_info = self.settings_service.get_notification_info(request.user)
        return Response(status=200, data=NotificationSerializer(notification_info).data)

    @extend_schema(responses={200: NotificationSerializer})
    @action(detail=False, methods=['put'], url_path='notifications/update')
    def update_notification_info(self, request):
        data = JSONParser().parse(request)
        serializer = NotificationSerializer
        stores = self.settings_service.update_notification_info(
            request.user, serializer.validated_data(data)
        )
        return Response(status=200, data=stores)
