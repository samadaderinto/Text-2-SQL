import json
import logging


from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from django.core.files.storage import default_storage
from django.http import HttpResponse


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import action, parser_classes
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


from .models import Customer, Order, Product, QueueJob, Store, User
from .permissions import ServerAccessPolicy
from .serializers import (
    AdminSerializer,
    CustomerSerializer,
    EmailSerializer,
    FileSerializer,
    LogOutSerializer,
    LoginSerializer,
    NotificationSerializer,
    OrderSerializer,
    ProductSerializer,
    QueryPlanSerializer,
    ResetPasswordSerializer,
    SearchSerializer,
    StoreSerializer,
    UserSerializer,
)
from .services import (
    AuthService,
    CustomerService,
    OrderService,
    ProductService,
    SearchService,
    SettingsService,
    StoreService,
)
from .job_queue import enqueue_job

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from kink import di

from utils.algorithms import TokenGenerator

logger = logging.getLogger(__name__)


def decode_uidb64(uidb64):
    try:
        user_id = smart_str(urlsafe_base64_decode(uidb64))
    except (ValueError, UnicodeDecodeError) as exc:
        raise serializers.ValidationError({"uidb64": "Invalid user identifier."}) from exc
    if not user_id:
        raise serializers.ValidationError({"uidb64": "Invalid user identifier."})
    try:
        return User._meta.pk.to_python(user_id)
    except (DjangoValidationError, TypeError, ValueError) as exc:
        raise serializers.ValidationError({"uidb64": "Invalid user identifier."}) from exc


def parse_positive_int(value, default, field_name):
    if value is None or value == "":
        value = default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise serializers.ValidationError({field_name: "Must be a valid integer."})
    if parsed < 1:
        raise serializers.ValidationError({field_name: "Must be greater than 0."})
    return parsed


def parse_non_negative_int(value, default, field_name):
    if value is None or value == "":
        value = default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise serializers.ValidationError({field_name: "Must be a valid integer."})
    if parsed < 0:
        raise serializers.ValidationError({field_name: "Must be greater than or equal to 0."})
    return parsed


def search_owned_records(
    search_service,
    resource,
    model,
    owner_filter,
    user,
    query,
    offset,
    limit,
    filters=None,
):
    ids, total = search_service.search_records(
        resource,
        user,
        query=query,
        offset=offset,
        limit=limit,
        filters=filters,
    )
    records = model.objects.filter(
        **{owner_filter: user},
        pk__in=ids,
    ).in_bulk()
    ordered_records = []
    for record_id in ids:
        primary_key = model._meta.pk.to_python(record_id)
        if primary_key in records:
            ordered_records.append(records[primary_key])
    return ordered_records, total


class AuthViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service: AuthService = di[AuthService]
        self.User = User

    permission_classes = (ServerAccessPolicy,)
    serializer_class = UserSerializer

    @extend_schema(request=UserSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        result = self.auth_service.create_user(
            request,
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )

        if not result:
            return Response(
                {"message": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"message": "User successfully created, Verify your email account"},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses={301: None})
    @action(
        detail=False,
        methods=["get"],
        url_path="activate/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)",
        name="activate",
    )
    def verify_activation(self, request, uidb64, token):
        user_id = decode_uidb64(uidb64)
        user = get_object_or_404(self.User, pk=user_id)

        if user.is_active:
            return Response(
                {"message": "Account is already activated"},
                status=status.HTTP_200_OK,
            )

        if not TokenGenerator().check_token(user, token):
            return Response(
                {"error": "Token is not valid, please request a new one"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return redirect(f"{settings.FRONTEND_URL}/auth/signin")

    @extend_schema(
        request=LogOutSerializer, responses={status.HTTP_205_RESET_CONTENT: None}
    )
    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        data = JSONParser().parse(request)
        serializer = LogOutSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
        except (InvalidToken, TokenError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        refresh.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        data = JSONParser().parse(request)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        data = self.auth_service.login_user(
            request,
            serializer.validated_data["email"],
            serializer.validated_data["password"],
        )
        if data.get("verify"):
            return Response(status=403, data={"message": data["verify"]})
        elif data.get("token") and data.get("data"):
            return Response(status=status.HTTP_200_OK, data=data)

        elif data.get("invalid_info", None):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Invalid user information"},
            )

    @extend_schema(
        request=LogOutSerializer, responses={status.HTTP_205_RESET_CONTENT: None}
    )
    @action(detail=False, methods=["post"], url_path="refresh-token")
    def refresh_token(self, request):
        data = JSONParser().parse(request)
        serializer = LogOutSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get("refresh")
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token

            return Response({"access": str(access_token), "refresh": str(refresh)})
        except (InvalidToken, TokenError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=EmailSerializer, responses={status.HTTP_200_OK: dict})
    @action(detail=False, methods=["post"], url_path="reset-password/request")
    def request_reset_password(self, request):
        data = JSONParser().parse(request)
        serializer = EmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = self.User.objects.filter(email=email).first()
        if user is not None:
            enqueue_job(
                QueueJob.Kind.EMAIL_PASSWORD_RESET,
                {
                    "user_id": user.pk,
                    "api_origin": request.build_absolute_uri("/").rstrip("/"),
                },
                user=user,
            )
        return Response(
            {
                "success": (
                    "If an account exists for this email address, a reset link "
                    "will be sent."
                )
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={status.HTTP_200_OK: None})
    @action(
        detail=False,
        methods=["get"],
        url_path="reset-password/verify/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)",
    )
    def verify_password_reset_token(self, request, uidb64, token):
        user_id = decode_uidb64(uidb64)
        user = get_object_or_404(self.User, pk=user_id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {"error": "Token is not valid, please request a new one"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return redirect(f"{settings.FRONTEND_URL}/auth/reset-password/{uidb64}/{token}")

    @extend_schema(request=ResetPasswordSerializer, responses={status.HTTP_205_RESET_CONTENT: None})
    @action(detail=False, methods=["post"], url_path="reset-password/reset")
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]
        message = self.auth_service.reset_password_user(
            request,
            new_password,
            uidb64=serializer.validated_data["uidb64"],
            token=serializer.validated_data["token"],
        )
        if message is None:
            return Response(
                {"error": "Token is not valid, please request a new one"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(data=message, status=status.HTTP_205_RESET_CONTENT)


class SearchViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service: SearchService = di[SearchService]

    permission_classes = (ServerAccessPolicy,)
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(request=SearchSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=["get", "post"], url_path="search")
    def elastic_searcher(self, request):
        if request.method == "GET":
            search_query = request.query_params.get("query", "")
        else:
            serializer = SearchSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            search_query = serializer.validated_data["search"]

        if not search_query:
            return Response(
                {"detail": "A search query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            search_results = self.search_service.elastic_search(search_query, request.user)
            return Response(data=search_results, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Elasticsearch search failed")
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @extend_schema(request=FileSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=["post"], url_path="upload")
    def audio_to_query(self, request):
        serializer = FileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        audio_file = serializer.validated_data["file"]
        file_path = default_storage.save(
            self.search_service.create_audio_upload_name(), audio_file
        )
        try:
            job = enqueue_job(
                QueueJob.Kind.QUERY_AUDIO,
                {"user_id": request.user.pk, "storage_path": file_path},
                user=request.user,
            )
        except Exception:
            default_storage.delete(file_path)
            raise
        return Response(
            {"job_id": str(job.pk), "status": job.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(request=QueryPlanSerializer, responses={status.HTTP_200_OK: None})
    @action(detail=False, methods=["post"], url_path="generate")
    def generate_query(self, request):
        serializer = QueryPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = enqueue_job(
            QueueJob.Kind.QUERY_GENERATE,
            {
                "user_id": request.user.pk,
                "prompt": serializer.validated_data["prompt"],
            },
            user=request.user,
        )
        return Response(
            {"job_id": str(job.pk), "status": job.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(responses={201: None})
    @action(detail=False, methods=["put"], url_path="upload/update")
    def confirm_update(self, request):
        try:
            result = self.search_service.confirm_and_execute_update(request.user, request.data)
            result_data = json.loads(result)
            response_status = (
                status.HTTP_200_OK
                if result_data.get("status") == "success"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(
                result_data,
                status=response_status,
            )
        except Exception as e:
            logger.error(f"Error in confirm_update: {str(e)}")
            return Response(
                {"status": "error", "message": "Failed to execute update."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(responses={205: None})
    @action(detail=False, methods=["delete"], url_path="upload/delete")
    def confirm_delete(self, request):
        try:
            result = self.search_service.confirm_and_execute_delete(request.user)
            result_data = json.loads(result)
            response_status = (
                status.HTTP_205_RESET_CONTENT
                if result_data.get("status") == "success"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(
                result_data,
                status=response_status,
            )
        except Exception as e:
            logger.error(f"Error in confirm_delete: {str(e)}")
            return Response(
                {"status": "error", "message": "Failed to execute delete."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(responses={201: None})
    @action(detail=False, methods=["post"], url_path="upload/create")
    def confirm_create(self, request):
        try:
            result = self.search_service.confirm_and_execute_create(request.user, request.data)
            result_data = json.loads(result)
            response_status = (
                status.HTTP_201_CREATED
                if result_data.get("status") == "success"
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(
                result_data,
                status=response_status,
            )
        except Exception as e:
            logger.error(f"Error in confirm_create: {str(e)}")
            return Response(
                {"status": "error", "message": "Failed to execute create."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductViewSet(viewsets.GenericViewSet):
    permission_classes = (ServerAccessPolicy,)
    serializer_class = ProductSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_service: ProductService = di[ProductService]
        self.search_service: SearchService = di[SearchService]

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    @action(detail=False, methods=["post"], url_path="create")
    @parser_classes([MultiPartParser])
    def create_product(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.product_service.create_product(request.user, serializer)
        return Response(status=201, data=product)

    @extend_schema(request=ProductSerializer, responses={200: ProductSerializer})
    @action(detail=False, methods=["put"], url_path="update")
    def update_product(self, request, pk=None):
        product = self.product_service.update_product(request.user, request.data)
        return Response(status=200, data=product)

    @extend_schema(responses={200: ProductSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="search")
    def retrieve_product(self, request):
        query = request.GET.get("query", "")
        page_number = parse_positive_int(request.GET.get("offset", 1), 1, "offset")
        per_page = parse_positive_int(request.GET.get("limit", 15), 15, "limit")
        try:
            products, count = search_owned_records(
                self.search_service,
                "products",
                Product,
                "store__user",
                request.user,
                query,
                (page_number - 1) * per_page,
                per_page,
            )
        except Exception:
            logger.exception("Elasticsearch product search failed")
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = ProductSerializer(products, many=True)

        response_data = {
            "products": serializer.data,
            "count": count,
            "total_pages": max(1, (count + per_page - 1) // per_page),
            "current_page": page_number,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    @action(detail=False, methods=["delete"], url_path="delete/(?P<product_id>[^/.]+)")
    def delete_product(self, request, product_id):
        self.product_service.delete_product(request.user, product_id)
        return Response(status=204)


class CustomerViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_service: CustomerService = di[CustomerService]
        self.search_service: SearchService = di[SearchService]

    permission_classes = (ServerAccessPolicy,)

    @extend_schema(request=CustomerSerializer, responses={200: CustomerSerializer})
    @action(detail=False, methods=["post"], url_path="create")
    @parser_classes([MultiPartParser])
    def create_customer(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            customer = self.customer_service.create_customer(request.user, serializer)
            return Response(status=201, data=customer.data)
        except serializers.ValidationError as exc:
            return Response(status=400, data=exc.detail)

    @extend_schema(request=CustomerSerializer, responses={200: CustomerSerializer})
    @action(detail=False, methods=["put"], url_path="update")
    def update_customer(self, request):
        data = JSONParser().parse(request)
        customer = self.customer_service.update_customer(request.user, data)
        return Response(status=201, data=customer)

    @extend_schema(responses={200: CustomerSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="search")
    def retrieve_customer(self, request, pk=None):
        query = request.GET.get("query", "")
        page_number = parse_positive_int(request.GET.get("offset", 1), 1, "offset")
        per_page = parse_positive_int(request.GET.get("limit", 15), 15, "limit")
        try:
            customers, count = search_owned_records(
                self.search_service,
                "customers",
                Customer,
                "user",
                request.user,
                query,
                (page_number - 1) * per_page,
                per_page,
            )
        except Exception:
            logger.exception("Elasticsearch customer search failed")
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = CustomerSerializer(customers, many=True)
        return Response(
            {
                "count": count,
                "total_pages": max(1, (count + per_page - 1) // per_page),
                "current_page": page_number,
                "customers": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class StoreViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store_service: StoreService = di[StoreService]

    permission_classes = (ServerAccessPolicy,)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=["post"], url_path="create")
    def create_store(self, request):
        data = JSONParser().parse(request)
        serializer = StoreSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        customer = self.store_service.create_store(request, serializer.validated_data)
        return Response(status=201, data=customer)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=["put"], url_path="update")
    def update_store(self, request):
        data = JSONParser().parse(request)
        store = self.store_service.update_store(request, data)
        return Response(status=201, data=store)


class OrderViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service: OrderService = di[OrderService]
        self.search_service: SearchService = di[SearchService]

    permission_classes = (ServerAccessPolicy,)
    serializer_class = OrderSerializer

    @extend_schema(request=OrderSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = self.order_service.create_order(request, serializer)
        return Response(status=201, data=order)

    @extend_schema(responses={205: None})
    @action(detail=False, methods=["delete"], url_path="delete/(?P<order_id>[^/.]+)")
    def delete_order(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.delete()
        return Response(status=205)

    @extend_schema(request=OrderSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=["put"], url_path="update")
    def update_order(self, request):
        data = JSONParser().parse(request)
        customer = self.order_service.update_order(request.user, data)
        return Response(status=201, data=customer)

    @extend_schema(responses={200: OrderSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="search")
    def retrieve_order(self, request):
        query = request.GET.get("query", "")
        status_filter = request.GET.get("status", "")
        offset = parse_non_negative_int(request.GET.get("offset", 0), 0, "offset")
        limit = parse_positive_int(request.GET.get("limit", 15), 15, "limit")

        try:
            orders, count = search_owned_records(
                self.search_service,
                "orders",
                Order,
                "user",
                request.user,
                query,
                offset,
                limit,
                filters={"status": status_filter} if status_filter else None,
            )
        except Exception:
            logger.exception("Elasticsearch order search failed")
            return Response(
                {"detail": "Search service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = OrderSerializer(orders, many=True)
        return Response(
            {
                "count": count,
                "total_pages": max(1, (count + limit - 1) // limit),
                "current_page": (offset // limit) + 1,
                "orders": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses={200: None})
    @action(detail=False, methods=["get"], url_path="download")
    def download_orders(self, request):
        job = enqueue_job(
            QueueJob.Kind.ORDERS_EXPORT,
            {"user_id": request.user.pk},
            user=request.user,
        )
        return Response(
            {"job_id": str(job.pk), "status": job.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(responses={200: None})
    @action(detail=False, methods=["get"], url_path="download/(?P<order_id>[^/.]+)")
    def download_order(self, request, order_id):
        get_object_or_404(Order, id=order_id, user=request.user)
        job = enqueue_job(
            QueueJob.Kind.ORDERS_EXPORT,
            {"user_id": request.user.pk, "order_id": order_id},
            user=request.user,
        )
        return Response(
            {"job_id": str(job.pk), "status": job.status},
            status=status.HTTP_202_ACCEPTED,
        )


class QueueJobView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_job(self, job_id, user):
        return get_object_or_404(QueueJob, pk=job_id, user=user)


class QueueJobStatusView(QueueJobView):
    def get(self, request, job_id):
        job = self.get_job(job_id, request.user)
        response_data = {
            "job_id": str(job.pk),
            "kind": job.kind,
            "status": job.status,
        }
        if job.status == QueueJob.Status.SUCCEEDED:
            response_data["result"] = job.result
        elif job.status == QueueJob.Status.FAILED:
            response_data["error"] = job.error or "The background task failed."
        return Response(response_data, status=status.HTTP_200_OK)


class QueueJobDownloadView(QueueJobView):
    def get(self, request, job_id):
        job = self.get_job(job_id, request.user)
        if job.kind != QueueJob.Kind.ORDERS_EXPORT:
            return Response(
                {"detail": "This job does not contain an order export."},
                status=status.HTTP_409_CONFLICT,
            )
        if job.status == QueueJob.Status.FAILED:
            return Response(
                {"detail": job.error or "The background task failed."},
                status=status.HTTP_409_CONFLICT,
            )
        if job.status != QueueJob.Status.SUCCEEDED or not isinstance(job.result, dict):
            return Response(
                {"detail": "The export is not ready yet."},
                status=status.HTTP_409_CONFLICT,
            )
        content = job.result.get("content")
        filename = job.result.get("filename")
        if not isinstance(content, str) or not isinstance(filename, str):
            return Response(
                {"detail": "This job does not contain a downloadable export."},
                status=status.HTTP_409_CONFLICT,
            )
        response = HttpResponse(content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class SettingsViewSet(viewsets.GenericViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_service: SettingsService = di[SettingsService]
        self.store_service: StoreService = di[StoreService]

    permission_classes = (ServerAccessPolicy,)

    @extend_schema(responses={200: AdminSerializer})
    @action(detail=False, methods=["get"], url_path="admin/get")
    def get_admin(self, request):
        admin_info = self.settings_service.get_admin_info(request.user.email)
        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(request=UserSerializer, responses={201: AdminSerializer})
    @action(detail=False, methods=["put"], url_path="admin/update")
    def edit_admin_info(self, request):
        data = JSONParser().parse(request)

        admin_info = self.settings_service.edit_admin_info(request.user.email, data)

        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(responses={200: StoreSerializer})
    @action(detail=False, methods=["get"], url_path="store/get")
    def get_store(self, request):
        store = get_object_or_404(Store, user=request.user)

        return Response(status=200, data=StoreSerializer(store).data)

    @extend_schema(request=StoreSerializer, responses={200: StoreSerializer})
    @action(detail=False, methods=["put"], url_path="store/update")
    def update_store(self, request):
        data = JSONParser().parse(request)
        store = self.store_service.partially_update_store(request, data)
        return Response(status=201, data=store)

    @extend_schema(responses={200: NotificationSerializer})
    @action(detail=False, methods=["get"], url_path="notifications/get")
    def get_notification_info(self, request):
        notification_info = self.settings_service.get_notification_info(request.user)
        return Response(status=200, data=NotificationSerializer(notification_info).data)

    @extend_schema(responses={200: NotificationSerializer})
    @action(detail=False, methods=["put"], url_path="notifications/update")
    def update_notification_info(self, request):
        data = JSONParser().parse(request)
        settings_data = self.settings_service.update_notification_info(request.user, data)
        return Response(status=200, data=settings_data)
