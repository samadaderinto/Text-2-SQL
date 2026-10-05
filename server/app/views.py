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


from .models import Customer, NotificationDevice, Order, Product, QueueJob, Store, User
from .permissions import ServerAccessPolicy
from .serializers import (
    AdminSerializer,
    CustomerSearchResponseSerializer,
    CustomerSerializer,
    EmailSerializer,
    ErrorResponseSerializer,
    FileSerializer,
    JobAcceptedResponseSerializer,
    LogOutSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    MessageResponseSerializer,
    MutationConfirmationResponseSerializer,
    NotificationSerializer,
    NotificationDeviceSerializer,
    OrderSearchResponseSerializer,
    OrderSerializer,
    ProductSearchResponseSerializer,
    ProductSerializer,
    QueryPlanSerializer,
    QueueJobStatusResponseSerializer,
    ResetPasswordSerializer,
    SearchSerializer,
    StoreSerializer,
    TokenRefreshResponseSerializer,
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
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, OpenApiTypes, extend_schema
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

    @extend_schema(
        summary="Register new merchant user account",
        description=(
            "Creates a new merchant user profile with email and password credentials. "
            "Generates an unverified account and dispatches an activation link to the user's email. "
            "Compare with `/auth/login/`, which authenticates users after their accounts have been activated."
        ),
        request=UserSerializer,
        responses={
            201: OpenApiResponse(response=MessageResponseSerializer, description="User successfully registered; activation email sent"),
            400: OpenApiResponse(response=MessageResponseSerializer, description="Validation failure or email already registered"),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Verify and activate user account",
        description=(
            "Validates the one-time activation token delivered in the welcome email. "
            "Upon success, marks the account as active and redirects the user (HTTP 302) to the frontend sign-in view. "
            "Compare with `/auth/signup/`, which initiates account registration and generates this token."
        ),
        parameters=[
            OpenApiParameter(
                name="uidb64",
                type=str,
                location=OpenApiParameter.PATH,
                description="Base64-encoded user ID",
            ),
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.PATH,
                description="One-time activation cryptographic token",
            ),
        ],
        responses={
            302: OpenApiResponse(description="Redirects to frontend signin page"),
            200: OpenApiResponse(response=MessageResponseSerializer, description="Account is already activated"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid or expired activation token"),
            404: OpenApiResponse(description="User not found for supplied uidb64"),
        },
        tags=["Authentication"],
    )
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
        summary="Log out and blacklist refresh token",
        description=(
            "Blacklists the submitted JWT refresh token, preventing any further access token renewals from it. "
            "Clients should discard stored access and refresh tokens upon calling this endpoint. "
            "Compare with `/auth/refresh-token/`, which continues an active session."
        ),
        request=LogOutSerializer,
        responses={
            205: OpenApiResponse(description="Session invalidated and refresh token blacklisted"),
            400: OpenApiResponse(description="Invalid or expired refresh token"),
        },
        tags=["Authentication"],
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

    @extend_schema(
        summary="Authenticate credentials and issue JWT pair",
        description=(
            "Authenticates user credentials (email and password). Returns user profile data "
            "along with a JWT access token (1-day validity) and refresh token (7-day validity). "
            "If the account has not yet completed email activation, returns HTTP 403. "
            "Compare with `/auth/refresh-token/`, which renews access without re-submitting user passwords."
        ),
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(response=LoginResponseSerializer, description="Authentication successful, tokens issued"),
            400: OpenApiResponse(response=MessageResponseSerializer, description="Invalid email or password"),
            403: OpenApiResponse(response=MessageResponseSerializer, description="Email verification required"),
        },
        tags=["Authentication"],
    )
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
        summary="Renew JWT access token",
        description=(
            "Issues a fresh JWT access token using a valid, unexpired refresh token. "
            "Allows the client application to refresh expired access tokens seamlessly without prompting user credentials. "
            "Compare with `/auth/login/`, which performs primary credential authentication."
        ),
        request=LogOutSerializer,
        responses={
            200: OpenApiResponse(response=TokenRefreshResponseSerializer, description="Access token successfully refreshed"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid, expired, or blacklisted refresh token"),
        },
        tags=["Authentication"],
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

    @extend_schema(
        summary="Request password reset email",
        description=(
            "Initiates the password reset workflow by enqueuing a background task (`EMAIL_PASSWORD_RESET`) "
            "to deliver a password recovery email if the email is associated with a registered account. "
            "Always responds with HTTP 200 and a generic message to prevent account enumeration. "
            "Compare with `/auth/reset-password/reset/`, which consumes the generated token."
        ),
        request=EmailSerializer,
        responses={
            200: OpenApiResponse(response=MessageResponseSerializer, description="Reset instructions sent if email exists"),
            400: OpenApiResponse(description="Validation error in email address format"),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Validate password reset link token",
        description=(
            "Validates the one-time password recovery cryptographic token against the user ID. "
            "If valid, redirects (HTTP 302) to the frontend password reset interface (`/auth/reset-password/{uidb64}/{token}`). "
            "If invalid or expired, returns HTTP 401 Unauthorized."
        ),
        parameters=[
            OpenApiParameter(
                name="uidb64",
                type=str,
                location=OpenApiParameter.PATH,
                description="Base64-encoded user ID",
            ),
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.PATH,
                description="Password reset token from email link",
            ),
        ],
        responses={
            302: OpenApiResponse(description="Redirects to frontend password reset page"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid or expired token"),
            404: OpenApiResponse(description="User not found for given uidb64"),
        },
        tags=["Authentication"],
    )
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

    @extend_schema(
        summary="Confirm and apply new password",
        description=(
            "Consumes the reset token, user ID (`uidb64`), and new password to update the user account password. "
            "Returns HTTP 205 Reset Content upon successful password change. "
            "Compare with `/auth/reset-password/request/`, which initiates the reset request."
        ),
        request=ResetPasswordSerializer,
        responses={
            205: OpenApiResponse(description="Password successfully changed"),
            400: OpenApiResponse(description="Validation error in password complexity or missing fields"),
            401: OpenApiResponse(response=ErrorResponseSerializer, description="Invalid or expired reset token"),
        },
        tags=["Authentication"],
    )
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
    serializer_class = SearchSerializer

    @extend_schema(
        summary="Search owned store data via Elasticsearch",
        description=(
            "Executes synchronous lexical and fuzzy search across products, customers, and orders owned by the user. "
            "Accepts `query` as a URL query parameter for GET requests, or `search` in the JSON request body for POST requests. "
            "Unlike `/query/generate/` (which translates conversational English into SQL via LLMs) or "
            "`/query/upload/` (which transcribes speech audio into queries asynchronously), this endpoint performs fast, "
            "direct search against pre-indexed Elasticsearch documents."
        ),
        parameters=[
            OpenApiParameter(
                name="query",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search query string for GET requests",
            ),
        ],
        request=SearchSerializer,
        responses={
            200: OpenApiResponse(description="Matching records across products, customers, and orders"),
            400: OpenApiResponse(response=ErrorResponseSerializer, description="Search query string is required"),
            503: OpenApiResponse(response=ErrorResponseSerializer, description="Elasticsearch service temporarily unavailable"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Upload speech audio for voice-to-SQL processing",
        description=(
            "Accepts a recorded audio file (e.g. WAV, MP3, WebM) containing a spoken query or operational command "
            "(e.g. 'Show me pending orders above $200 from last week'). "
            "Persists the audio to storage and enqueues an asynchronous queue job (`QUERY_AUDIO`) that transcribes speech, "
            "interprets user intent, and generates a structured query plan. "
            "Returns HTTP 202 Accepted with a `job_id`. Poll `/jobs/{job_id}/` until status is `succeeded` to retrieve results. "
            "Compare with `/query/generate/` (which accepts typed text prompts directly) and `/query/search/` (which runs synchronous Elasticsearch queries)."
        ),
        request=FileSerializer,
        responses={
            202: OpenApiResponse(response=JobAcceptedResponseSerializer, description="Audio job enqueued successfully"),
            400: OpenApiResponse(description="Invalid audio file upload or unsupported format"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Generate SQL query plan from text prompt",
        description=(
            "Submits a natural language text prompt (e.g. 'List my top 5 customers by sales volume'). "
            "Enqueues an asynchronous queue job (`QUERY_GENERATE`) where LLMs formulate the query against the schema. "
            "Returns HTTP 202 Accepted with a `job_id`. Poll `/jobs/{job_id}/` until status is `succeeded` to retrieve results. "
            "Compare with `/query/upload/` (which processes voice audio recordings) and `/query/search/` (which performs Elasticsearch keyword search)."
        ),
        request=QueryPlanSerializer,
        responses={
            202: OpenApiResponse(response=JobAcceptedResponseSerializer, description="Query generation job enqueued successfully"),
            400: OpenApiResponse(description="Prompt text is required"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Confirm and execute staged update mutation",
        description=(
            "Confirms and applies a data update staged by the conversational assistant during a prior voice or NLP query session. "
            "Unlike direct REST updates (e.g. `/product/update/`, `/orders/update/`), this endpoint executes mutations "
            "staged in user query sessions after explicit confirmation. "
            "Returns HTTP 200 on success or HTTP 400 on execution failure."
        ),
        responses={
            200: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged update applied successfully"),
            400: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged update execution failed or rejected"),
            500: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Internal error executing update"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Confirm and execute staged delete mutation",
        description=(
            "Confirms and commits a record deletion staged by the conversational assistant during a voice or NLP query session. "
            "Unlike direct REST deletion (e.g. `/product/delete/{product_id}/`, `/orders/delete/{order_id}/`), this endpoint "
            "finalizes deletions planned and staged by the AI assistant after user confirmation. "
            "Returns HTTP 205 Reset Content upon successful execution."
        ),
        responses={
            205: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged deletion executed successfully"),
            400: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged deletion rejected or invalid"),
            500: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Internal error executing deletion"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Confirm and execute staged create mutation",
        description=(
            "Confirms and persists a new record creation staged by the conversational assistant during a voice or NLP query session. "
            "Unlike direct REST creation endpoints (e.g. `/product/create/`, `/orders/create/`), this endpoint confirms "
            "and saves new records synthesized from natural language interaction. "
            "Returns HTTP 201 Created on success."
        ),
        responses={
            201: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged record created successfully"),
            400: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Staged creation rejected or invalid"),
            500: OpenApiResponse(response=MutationConfirmationResponseSerializer, description="Internal error executing create"),
        },
        tags=["Natural Language & Speech Query"],
    )
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

    @extend_schema(
        summary="Create catalog product",
        description=(
            "Adds a new product to the authenticated user's store catalog. Supports multipart form data for uploading "
            "product imagery, links the product to the merchant's store, and syncs to Elasticsearch. "
            "Compare with `/product/update/` and `/query/upload/create/`."
        ),
        request=ProductSerializer,
        responses={
            201: OpenApiResponse(response=ProductSerializer, description="Product created successfully"),
            400: OpenApiResponse(description="Validation error in product fields"),
        },
        tags=["Products"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    @parser_classes([MultiPartParser])
    def create_product(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.product_service.create_product(request.user, serializer)
        return Response(status=201, data=product)

    @extend_schema(
        summary="Update catalog product",
        description=(
            "Modifies attributes (title, description, price, category, availability) of an existing product owned by the user. "
            "Synchronizes changes to the Elasticsearch index. "
            "Compare with `/product/create/` and `/product/delete/{product_id}/`."
        ),
        request=ProductSerializer,
        responses={
            200: OpenApiResponse(response=ProductSerializer, description="Product updated successfully"),
            400: OpenApiResponse(description="Validation or update error"),
            404: OpenApiResponse(description="Product not found"),
        },
        tags=["Products"],
    )
    @action(detail=False, methods=["put"], url_path="update")
    def update_product(self, request, pk=None):
        product = self.product_service.update_product(request.user, request.data)
        return Response(status=200, data=product)

    @extend_schema(
        summary="Search and paginate store products",
        description=(
            "Searches products belonging to the authenticated merchant's store via Elasticsearch index. "
            "Supports text keyword query and 1-based pagination using `offset` (page number) and `limit` (page size). "
            "Compare with `/query/search/`, which searches across all resource domains (products, customers, orders) at once."
        ),
        parameters=[
            OpenApiParameter(
                name="query",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search keyword for product title and description",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=1,
                description="1-based page number (e.g. 1, 2, 3...)",
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=15,
                description="Number of products returned per page",
            ),
        ],
        responses={
            200: OpenApiResponse(response=ProductSearchResponseSerializer, description="Paginated product search results"),
            503: OpenApiResponse(response=ErrorResponseSerializer, description="Search service temporarily unavailable"),
        },
        tags=["Products"],
    )
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

    @extend_schema(
        summary="Delete catalog product by ID",
        description=(
            "Permanently removes a product belonging to the merchant's store from the database and search index. "
            "Returns HTTP 204 No Content upon deletion. "
            "Compare with `/product/update/`."
        ),
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Unique identifier of the product to delete",
            ),
        ],
        responses={
            204: OpenApiResponse(description="Product deleted successfully"),
            404: OpenApiResponse(description="Product not found or unauthorized"),
        },
        tags=["Products"],
    )
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
    serializer_class = CustomerSerializer

    @extend_schema(
        summary="Create customer record",
        description=(
            "Registers a new customer profile associated with the authenticated user's store and syncs to search index. "
            "Compare with `/customers/update/` and `/customers/search/`."
        ),
        request=CustomerSerializer,
        responses={
            201: OpenApiResponse(response=CustomerSerializer, description="Customer created successfully"),
            400: OpenApiResponse(description="Validation error in customer attributes"),
        },
        tags=["Customers"],
    )
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

    @extend_schema(
        summary="Update customer record",
        description=(
            "Updates contact details, name, or phone number of an existing customer record owned by the user. "
            "Compare with `/customers/create/`."
        ),
        request=CustomerSerializer,
        responses={
            201: OpenApiResponse(response=CustomerSerializer, description="Customer updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Customer not found"),
        },
        tags=["Customers"],
    )
    @action(detail=False, methods=["put"], url_path="update")
    def update_customer(self, request):
        data = JSONParser().parse(request)
        customer = self.customer_service.update_customer(request.user, data)
        return Response(status=201, data=customer)

    @extend_schema(
        summary="Search and paginate customer records",
        description=(
            "Searches customer records belonging to the merchant's store using Elasticsearch. "
            "Supports keyword query matching name, email, or phone number, with 1-based page pagination (`offset`, `limit`). "
            "Compare with `/query/search/` which searches globally across products, customers, and orders."
        ),
        parameters=[
            OpenApiParameter(
                name="query",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search keyword for customer name, email, or phone",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=1,
                description="1-based page number",
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=15,
                description="Number of customer records per page",
            ),
        ],
        responses={
            200: OpenApiResponse(response=CustomerSearchResponseSerializer, description="Paginated customer search results"),
            503: OpenApiResponse(response=ErrorResponseSerializer, description="Search service temporarily unavailable"),
        },
        tags=["Customers"],
    )
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
    serializer_class = StoreSerializer

    @extend_schema(
        summary="Create store profile",
        description=(
            "Creates an initial store profile linked to the merchant's account. "
            "Compare with `/settings/store/get/` and `/settings/store/update/`."
        ),
        request=StoreSerializer,
        responses={
            201: OpenApiResponse(response=StoreSerializer, description="Store created successfully"),
            400: OpenApiResponse(description="Validation error in store fields"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_store(self, request):
        data = JSONParser().parse(request)
        serializer = StoreSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        customer = self.store_service.create_store(request, serializer.validated_data)
        return Response(status=201, data=customer)

    @extend_schema(
        summary="Update store profile",
        description=(
            "Updates merchant store information (name, bio, contact details, currency). "
            "Compare with `/settings/store/update/`."
        ),
        request=StoreSerializer,
        responses={
            201: OpenApiResponse(response=StoreSerializer, description="Store updated successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Settings & Notifications"],
    )
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

    @extend_schema(
        summary="Create store order",
        description=(
            "Creates a new order record for the authenticated user's store, calculates cart totals, "
            "and updates the Elasticsearch index. "
            "Compare with `/orders/update/`."
        ),
        request=OrderSerializer,
        responses={
            201: OpenApiResponse(response=OrderSerializer, description="Order created successfully"),
            400: OpenApiResponse(description="Validation error in order contents"),
        },
        tags=["Orders"],
    )
    @action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = self.order_service.create_order(request, serializer)
        return Response(status=201, data=order)

    @extend_schema(
        summary="Delete store order by ID",
        description=(
            "Deletes an order record belonging to the authenticated merchant and removes it from search indexes. "
            "Returns HTTP 205 Reset Content upon successful deletion. "
            "Compare with `/orders/update/`."
        ),
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Unique identifier of the order to delete",
            ),
        ],
        responses={
            205: OpenApiResponse(description="Order deleted successfully"),
            404: OpenApiResponse(description="Order not found"),
        },
        tags=["Orders"],
    )
    @action(detail=False, methods=["delete"], url_path="delete/(?P<order_id>[^/.]+)")
    def delete_order(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.delete()
        return Response(status=205)

    @extend_schema(
        summary="Update store order",
        description=(
            "Updates order status, line items, or customer details for an existing order owned by the user. "
            "Compare with `/orders/create/` and `/orders/delete/{order_id}/`."
        ),
        request=OrderSerializer,
        responses={
            201: OpenApiResponse(response=OrderSerializer, description="Order updated successfully"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Order not found"),
        },
        tags=["Orders"],
    )
    @action(detail=False, methods=["put"], url_path="update")
    def update_order(self, request):
        data = JSONParser().parse(request)
        customer = self.order_service.update_order(request.user, data)
        return Response(status=201, data=customer)

    @extend_schema(
        summary="Search and filter store orders",
        description=(
            "Searches and filters orders owned by the merchant using Elasticsearch. "
            "Supports full-text query, exact status filter (e.g. pending, completed, cancelled), "
            "and 0-based record offset and limit pagination. "
            "Compare with `/orders/download/` which exports orders to a downloadable CSV spreadsheet."
        ),
        parameters=[
            OpenApiParameter(
                name="query",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Search keyword for order items or customer details",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter orders by status string (e.g. pending, completed, cancelled)",
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=0,
                description="0-based record offset",
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                default=15,
                description="Number of orders to retrieve",
            ),
        ],
        responses={
            200: OpenApiResponse(response=OrderSearchResponseSerializer, description="Paginated order search results"),
            503: OpenApiResponse(response=ErrorResponseSerializer, description="Search service temporarily unavailable"),
        },
        tags=["Orders"],
    )
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

    @extend_schema(
        operation_id="orders_export_all_csv",
        summary="Queue CSV export for all store orders",
        description=(
            "Enqueues an asynchronous background job (`ORDERS_EXPORT`) to compile all store orders into a CSV spreadsheet. "
            "Returns HTTP 202 Accepted with a `job_id`. Once the job is succeeded, "
            "download the generated CSV file directly via `/jobs/{job_id}/download/`. "
            "Compare with `/orders/download/{order_id}/`, which exports only a single order."
        ),
        responses={
            202: OpenApiResponse(response=JobAcceptedResponseSerializer, description="CSV export job queued"),
        },
        tags=["Orders"],
    )
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

    @extend_schema(
        operation_id="orders_export_single_csv",
        summary="Queue CSV export for a single order",
        description=(
            "Enqueues an asynchronous background job (`ORDERS_EXPORT`) to generate a CSV export for a specific order by ID. "
            "Returns HTTP 202 Accepted with a `job_id`. Once ready, retrieve the CSV file from `/jobs/{job_id}/download/`. "
            "Compare with `/orders/download/` which exports all store orders."
        ),
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Unique identifier of the order to export",
            ),
        ],
        responses={
            202: OpenApiResponse(response=JobAcceptedResponseSerializer, description="CSV export job queued"),
            404: OpenApiResponse(description="Order not found"),
        },
        tags=["Orders"],
    )
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
    serializer_class = QueueJobStatusResponseSerializer

    @extend_schema(
        summary="Get background job status and result",
        description=(
            "Polls the execution status (`pending`, `processing`, `succeeded`, `failed`) and output of an asynchronous queue job. "
            "Jobs are created by asynchronous endpoints such as `/query/upload/` (speech-to-text), "
            "`/query/generate/` (text query plan), and `/orders/download/` (CSV export). "
            "When status is `succeeded`, `result` contains the payload. "
            "When status is `failed`, `error` contains details. "
            "Compare with `/jobs/{job_id}/download/`, which streams downloadable CSV file content "
            "directly rather than returning JSON status."
        ),
        parameters=[
            OpenApiParameter(
                name="job_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the background queue job",
            ),
        ],
        responses={
            200: OpenApiResponse(response=QueueJobStatusResponseSerializer, description="Job status and payload"),
            404: OpenApiResponse(description="Job not found or does not belong to the current user"),
        },
        tags=["Background Jobs"],
    )
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
    @extend_schema(
        summary="Download completed order export CSV file",
        description=(
            "Streams the CSV file generated by an `ORDERS_EXPORT` background job. "
            "Initiated via `/orders/download/` (all orders) or `/orders/download/{order_id}/` (single order). "
            "If the job has not finished yet, is not an order export, or has failed, returns HTTP 409 Conflict. "
            "Compare with `/jobs/{job_id}/`, which checks job status metadata as JSON without streaming the file."
        ),
        parameters=[
            OpenApiParameter(
                name="job_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="UUID of the completed export job",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="CSV spreadsheet file stream",
            ),
            404: OpenApiResponse(description="Job not found or unauthorized"),
            409: OpenApiResponse(response=ErrorResponseSerializer, description="Export not ready, failed, or invalid job kind"),
        },
        tags=["Background Jobs"],
    )
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
    serializer_class = StoreSerializer

    @extend_schema(
        summary="Retrieve administrator profile",
        description=(
            "Fetches administrative user details (first name, email) for the authenticated merchant account. "
            "Compare with `/settings/admin/update/`."
        ),
        responses={
            200: OpenApiResponse(response=AdminSerializer, description="Admin profile details"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["get"], url_path="admin/get")
    def get_admin(self, request):
        admin_info = self.settings_service.get_admin_info(request.user.email)
        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(
        summary="Update administrator profile",
        description=(
            "Updates administrative profile information for the authenticated merchant account. "
            "Compare with `/settings/admin/get/`."
        ),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(response=AdminSerializer, description="Admin profile updated successfully"),
            400: OpenApiResponse(description="Validation error in updated fields"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["put"], url_path="admin/update")
    def edit_admin_info(self, request):
        data = JSONParser().parse(request)

        admin_info = self.settings_service.edit_admin_info(request.user.email, data)

        return Response(status=200, data=AdminSerializer(admin_info).data)

    @extend_schema(
        summary="Retrieve store settings and profile",
        description=(
            "Retrieves configuration details for the user's merchant store (name, bio, currency, contact phone). "
            "Compare with `/settings/store/update/`."
        ),
        responses={
            200: OpenApiResponse(response=StoreSerializer, description="Store profile details"),
            404: OpenApiResponse(description="Store profile not found"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["get"], url_path="store/get")
    def get_store(self, request):
        store = get_object_or_404(Store, user=request.user)

        return Response(status=200, data=StoreSerializer(store).data)

    @extend_schema(
        summary="Update store settings and profile",
        description=(
            "Partially updates store profile fields (name, bio, currency, phone). "
            "Compare with `/settings/store/get/`."
        ),
        request=StoreSerializer,
        responses={
            201: OpenApiResponse(response=StoreSerializer, description="Store settings updated successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["put"], url_path="store/update")
    def update_store(self, request):
        data = JSONParser().parse(request)
        store = self.store_service.partially_update_store(request, data)
        return Response(status=201, data=store)

    @extend_schema(
        summary="Retrieve notification channel preferences",
        description=(
            "Retrieves active notification preferences (email notification and push notification flags) for the merchant. "
            "Compare with `/settings/notifications/update/`."
        ),
        responses={
            200: OpenApiResponse(response=NotificationSerializer, description="Active notification channel flags"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["get"], url_path="notifications/get")
    def get_notification_info(self, request):
        notification_info = self.settings_service.get_notification_info(request.user)
        return Response(status=200, data=NotificationSerializer(notification_info).data)

    @extend_schema(
        summary="Update notification channel preferences",
        description=(
            "Updates preferences for email and push notifications. "
            "Compare with `/settings/notifications/get/` and `/settings/notifications/devices/`."
        ),
        request=NotificationSerializer,
        responses={
            200: OpenApiResponse(response=NotificationSerializer, description="Notification preferences updated successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["put"], url_path="notifications/update")
    def update_notification_info(self, request):
        data = JSONParser().parse(request)
        settings_data = self.settings_service.update_notification_info(request.user, data)
        return Response(status=200, data=settings_data)

    @extend_schema(
        summary="Register push notification device token",
        description=(
            "Registers or updates a Firebase Cloud Messaging (FCM) device registration token associated with the user account "
            "for web or mobile push notification delivery. "
            "Compare with DELETE `/settings/notifications/devices/` to revoke a device token."
        ),
        request=NotificationDeviceSerializer,
        responses={
            201: OpenApiResponse(response=NotificationDeviceSerializer, description="Device token registered successfully"),
            400: OpenApiResponse(description="Invalid device registration payload"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["post"], url_path="notifications/devices")
    def register_notification_device(self, request):
        serializer = NotificationDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device, _ = NotificationDevice.objects.update_or_create(
            token=serializer.validated_data["token"],
            defaults={
                "user": request.user,
                "platform": serializer.validated_data.get("platform", "web"),
                "is_active": True,
            },
        )
        return Response(status=status.HTTP_201_CREATED, data=NotificationDeviceSerializer(device).data)

    @extend_schema(
        summary="Unregister push notification device token",
        description=(
            "Deactivates an FCM device push token so the device no longer receives push notifications. "
            "Compare with POST `/settings/notifications/devices/` which registers or refreshes a device token."
        ),
        request=NotificationDeviceSerializer,
        responses={
            204: OpenApiResponse(description="Device token deactivated successfully"),
            400: OpenApiResponse(description="Invalid request payload"),
        },
        tags=["Settings & Notifications"],
    )
    @action(detail=False, methods=["delete"], url_path="notifications/devices")
    def unregister_notification_device(self, request):
        serializer = NotificationDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        NotificationDevice.objects.filter(
            user=request.user,
            token=serializer.validated_data["token"],
        ).update(is_active=False)
        return Response(status=status.HTTP_204_NO_CONTENT)
