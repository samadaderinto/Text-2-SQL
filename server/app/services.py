import json
import logging
import uuid


from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, smart_str
from django.db.models import Q
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction

from typing import Type
from openai import OpenAI
from rest_framework import serializers, status
from rest_framework.response import Response


from utils.algorithms import TokenGenerator, auth_token
from .search_index import SEARCH_DEFINITIONS, ensure_search_indices, get_elasticsearch_client

from .serializers import (
    CustomerSerializer,
    NotificationSerializer,
    OrderSerializer,
    ProductSerializer,
    StoreSerializer,
    UserSerializer,
)
from .models import Customer, Notification, Order, Product, Store, User

logger = logging.getLogger(__name__)

QUERY_RESOURCES = {
    "products": {
        "model": Product,
        "serializer": ProductSerializer,
        "owner_filter": "store__user",
        "search_fields": ["title", "description", "category"],
        "filter_fields": {"title", "description", "category", "available", "price", "currency"},
        "sort_fields": {"created", "updated", "price", "title", "available", "sales"},
    },
    "orders": {
        "model": Order,
        "serializer": OrderSerializer,
        "owner_filter": "user",
        "search_fields": ["id", "status"],
        "filter_fields": {"id", "status", "total", "subtotal"},
        "sort_fields": {"created", "updated", "total", "subtotal", "status"},
    },
    "customers": {
        "model": Customer,
        "serializer": CustomerSerializer,
        "owner_filter": "user",
        "search_fields": ["first_name", "last_name", "email", "phone_number"],
        "filter_fields": {"first_name", "last_name", "email", "phone_number", "is_active"},
        "sort_fields": {"created", "updated", "first_name", "last_name", "email"},
    },
}


class AuthService:
    def __init__(
        self, User: Type[User], Store: Type[Store], Notification: Type[Notification]
    ):
        self.User = User
        self.Store = Store
        self.Notification = Notification

    def get_base_url(self, request):
        scheme = request.scheme
        host = request.get_host()
        return f"{scheme}://{host}"

    def send_activation_mail(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = TokenGenerator().make_token(user)
        link = f"{self.get_base_url(request)}/auth/activate/{uidb64}/{token}/"
        absolute_url = request.build_absolute_uri(link)

        send_mail(
            f"Welcome, {email}",
            f"This is the link to verify your email. {absolute_url}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

    @transaction.atomic
    def create_user(self, request, email, password):
        if self.User.objects.filter(email=email).exists():
            return None

        user = self.User.objects.create_user(email=email, password=password)
        self.Store.objects.create(user=user, email=email, name=email, bio="")
        self.Notification.objects.create(user=user)
        self.send_activation_mail(request, email)
        return user

    def login_user(self, request, email, password):
        user = authenticate(request, username=email, password=password)

        if user and user.is_active:
            token = auth_token(user)
            serializer = UserSerializer(user)
            return {"token": token, "data": serializer.data}

        inactive_user = self.User.objects.filter(email=email, is_active=False).first()
        if inactive_user and inactive_user.check_password(password):
            return {"verify": "Please verify your email account"}

        return {"invalid_info": "Invalid user information"}

    def request_reset_password_user(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = (
            f"{self.get_base_url(request)}/auth/reset-password/verify/{uidb64}/{token}/"
        )

        return request.build_absolute_uri(link)

    def reset_password_user(self, request, new_password, uidb64, token):
        try:
            user_id = self.User._meta.pk.to_python(
                smart_str(urlsafe_base64_decode(uidb64))
            )
        except (TypeError, ValueError, UnicodeDecodeError):
            return None
        user = self.User.objects.filter(pk=user_id).first()
        if user is None:
            return None
        if not PasswordResetTokenGenerator().check_token(user, token):
            return None

        user.set_password(new_password)
        user.save()

        return {"success": "Password updated successfully"}


class StoreService:
    def __init__(self, User: Type[User], Store: Type[Store]):
        self.User = User
        self.Store = Store

    def create_store(self, request, data):
        user = request.user
        store, _ = self.Store.objects.get_or_create(user=user, defaults=data)
        serializer = StoreSerializer(store)
        return serializer.data

    def get_stores_by_user(self, request):
        stores = get_list_or_404(self.Store, user=request.user)
        serializer = StoreSerializer(stores, many=True)
        return serializer.data

    def delete_store(self, request):
        store = get_object_or_404(self.Store, user=request.user)
        store.delete()
        return {"success": "Store deleted successfully"}

    def update_store(self, request, data):
        store = get_object_or_404(self.Store, user=request.user)
        serializer = StoreSerializer(store, data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def partially_update_store(self, request, data):
        store = get_object_or_404(self.Store, user=request.user)
        serializer = StoreSerializer(store, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class SearchService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def search_records(
        self, resource, user, query="", offset=0, limit=15, filters=None
    ):
        definition = SEARCH_DEFINITIONS[resource]
        client = get_elasticsearch_client()
        ensure_search_indices(client, [resource])

        search_query = (
            {"multi_match": {"query": query, "fields": ["search_text"]}}
            if query
            else {"match_all": {}}
        )
        search_filters = [{"term": {"owner_id": str(user.pk)}}]
        for field, value in (filters or {}).items():
            search_filters.append({"term": {field: value}})

        response = client.search(
            index=definition["index"],
            query={"bool": {"must": [search_query], "filter": search_filters}},
            from_=offset,
            size=limit,
            sort=[{"_score": "desc"}, {"created": "desc"}],
            track_total_hits=True,
        )
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]
        if isinstance(total, dict):
            total = total["value"]
        return [hit["_id"] for hit in hits], total

    def elastic_search(self, search_query, user):
        client = get_elasticsearch_client()
        ensure_search_indices(client)
        response = client.search(
            index=",".join(
                definition["index"] for definition in SEARCH_DEFINITIONS.values()
            ),
            query={
                "bool": {
                    "must": [
                        {"multi_match": {"query": search_query, "fields": ["search_text"]}}
                    ],
                    "filter": [{"term": {"owner_id": str(user.pk)}}],
                }
            },
            size=100,
            track_total_hits=True,
        )
        hits = response["hits"]["hits"]
        result_data = [
            {"resource": hit["_index"].removeprefix("audql-"), **hit["_source"]}
            for hit in hits
        ]
        return {
            "status": "success",
            "data": result_data,
            "message": f"{len(result_data)} results found for query: {search_query}",
        }

    def parse_openai_response(self, response_json):
        try:
            response = json.loads(response_json)
            if (
                "choices" in response
                and response["choices"][0]["finish_reason"] == "stop"
            ):
                message_content = response["choices"][0]["message"]["content"]
                message_content = message_content.strip().strip("```").strip()
                if "Could you please provide more context or detail" in message_content:
                    return "The assistant needs more context or detail to generate the SQL query."
                return message_content
            else:
                return "The response was incomplete or there was an issue."
        except json.JSONDecodeError:
            logger.error("Error parsing JSON response")
            return "Error parsing the response from OpenAI."
        except KeyError:
            logger.error("Key error in OpenAI response")
            return "Error processing the response from OpenAI."
        except Exception:
            logger.error("Unexpected error processing the OpenAI response")
            return "Unexpected error processing the response."

    def audio_to_text(self, audio_data):
        if self.client is None:
            logger.error("OpenAI API key is not configured")
            return None
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data,
                response_format="text",
                language="en",
            )
            return response
        except Exception:
            logger.error("Error transcribing audio")
            return None

    def build_query_plan(self, text):
        if not text or not text.strip():
            raise ValueError("A query prompt is required.")
        if self.client is None:
            raise ValueError("Text-to-query service is not configured.")

        prompt = """
You convert store-admin requests into safe JSON query plans.
Return JSON only. No markdown.
Allowed resources: products, orders, customers.
Allowed intents: list, search, summarize.
Only read data. Never create, update, delete, or mention restricted/user/auth tables.
Schema:
{
  "intent": "list|search|summarize",
  "resource": "products|orders|customers",
  "search": "optional broad search text",
  "filters": {"field": "value"},
  "sort": "-created",
  "limit": 25
}
Use filters only for fields that naturally belong to that resource.
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=250,
        )
        response_json = response.to_dict()
        content = self.parse_openai_response(json.dumps(response_json))
        return self.normalize_query_plan(content)

    def normalize_query_plan(self, content):
        try:
            plan = json.loads(content.strip().strip("```").strip())
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("The query plan could not be parsed.") from exc

        if not isinstance(plan, dict):
            raise ValueError("The query plan must be a JSON object.")

        resource = str(plan.get("resource", "")).lower()
        intent = str(plan.get("intent", "search")).lower()
        if resource not in QUERY_RESOURCES:
            raise ValueError("Unsupported query resource.")
        if intent not in {"list", "search", "summarize"}:
            raise ValueError("Unsupported query intent.")

        filters = plan.get("filters", {})
        if filters is None:
            filters = {}
        if not isinstance(filters, dict):
            raise ValueError("Query plan filters must be a JSON object.")

        allowed_filters = QUERY_RESOURCES[resource]["filter_fields"]
        safe_filters = {
            field: value
            for field, value in filters.items()
            if field in allowed_filters and value not in [None, ""]
        }
        if any(
            not isinstance(value, (str, int, float, bool))
            for value in safe_filters.values()
        ):
            raise ValueError("Query plan filter values must be scalar.")

        sort = plan.get("sort") or "-created"
        sort_field = sort[1:] if isinstance(sort, str) and sort.startswith("-") else sort
        if (
            not isinstance(sort, str)
            or sort_field not in QUERY_RESOURCES[resource]["sort_fields"]
        ):
            sort = "-created"

        search = plan.get("search") or ""
        if not isinstance(search, str):
            raise ValueError("Query plan search text must be a string.")

        try:
            limit = int(plan.get("limit", 25))
        except (TypeError, ValueError):
            limit = 25
        limit = min(max(limit, 1), 100)

        return {
            "intent": intent,
            "resource": resource,
            "search": search.strip(),
            "filters": safe_filters,
            "sort": sort,
            "limit": limit,
        }

    def execute_query_plan(self, user, plan):
        config = QUERY_RESOURCES[plan["resource"]]
        queryset = config["model"].objects.filter(**{config["owner_filter"]: user})

        search = plan.get("search")
        if search:
            search_filter = Q()
            for field in config["search_fields"]:
                search_filter |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(search_filter)

        for field, value in plan.get("filters", {}).items():
            if field in config["search_fields"]:
                queryset = queryset.filter(**{f"{field}__icontains": value})
            else:
                queryset = queryset.filter(**{field: value})

        queryset = queryset.order_by(plan["sort"])
        total_count = queryset.count()
        rows = list(queryset[: plan["limit"]])
        serializer = config["serializer"](rows, many=True)
        sql_preview = str(queryset.query)

        return {
            "status": "success",
            "message": f"Found {len(rows)} {plan['resource']}.",
            "plan": plan,
            "sql_preview": sql_preview,
            "total_count": total_count,
            "results": serializer.data,
        }

    def generate_query_response(self, user, text):
        plan = self.build_query_plan(text)
        response = self.execute_query_plan(user, plan)
        response["transcript"] = text
        return response

    def generate_query_response_from_audio(self, user, audio_data):
        transcript = self.audio_to_text(audio_data)
        if not transcript:
            raise ValueError("Audio could not be transcribed.")
        return self.generate_query_response(user, transcript)

    @staticmethod
    def create_audio_upload_name():
        return f"uploads/audio/{uuid.uuid4()}.webm"

    def confirm_and_execute_update(self, user, validated_data):
        return json.dumps(
            {
                "status": "error",
                "message": "Generated SQL execution is disabled. Use the typed update endpoints instead.",
            }
        )

    def confirm_and_execute_delete(self, user):
        return json.dumps(
            {
                "status": "error",
                "message": "Generated SQL execution is disabled. Use the typed delete endpoints instead.",
            }
        )

    def confirm_and_execute_create(self, user, validated_data=None):
        return json.dumps(
            {
                "status": "error",
                "message": "Generated SQL execution is disabled. Use the typed create endpoints instead.",
            }
        )

class ProductService:
    def __init__(self, User: Type[User], Product: Type[Product]):
        self.User = User
        self.Product = Product

    def get_products(self):
        product = get_object_or_404(self.Product)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_product(self, user, product_id):
        product = get_object_or_404(self.Product, pk=product_id, store__user=user)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)

    def create_product(self, user, serializer):
        store = get_object_or_404(Store, user=user)
        serializer.save(store=store)
        return serializer.data

    def update_product(self, user, data):
        product_id = data["id"]
        product = get_object_or_404(self.Product, pk=product_id, store__user=user)
        serializer = ProductSerializer(product, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class CustomerService:
    def __init__(self, User: Type[User], Customer: Type[Customer]):
        self.User = User
        self.Customer = Customer

    def get_customers(self, data):
        pass

    def get_customer(self, email, phone_number):
        customer = get_object_or_404(
            self.Customer, email=email, phone_number=phone_number
        )
        serializer = CustomerSerializer(customer)
        return serializer.data

    def create_customer(self, user, serializer):
        serializer.save(user=user)
        return serializer

    def update_customer(self, user, data):
        email = data["email"]
        phone_number = data["phone_number"]
        customer = get_object_or_404(
            self.Customer, user=user, email=email, phone_number=phone_number
        )
        serializer = CustomerSerializer(customer, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class OrderService:
    def __init__(self, User: Type[User], Order: Type[Order]):
        self.User = User
        self.Order = Order

    def get_orders(self, user):
        order = get_list_or_404(self.Order, user=user)
        return order

    def create_order(self, request, serializer):
        cart = serializer.validated_data.get("cart")
        if cart and cart.user != request.user:
            raise serializers.ValidationError({"cart": "Invalid cart for this user."})
        serializer.save(user=request.user)
        return serializer.data

    def update_order(self, user, data):
        id = data["id"]
        order = get_object_or_404(self.Order, id=id, user=user)
        serializer = OrderSerializer(order, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        cart = serializer.validated_data.get("cart")
        if cart and cart.user_id != user.id:
            raise serializers.ValidationError({"cart": "Invalid cart for this user."})
        serializer.save()
        return serializer.data


class SettingsService:
    def __init__(self, User: Type[User], Notification: Type[Notification]):
        self.User = User
        self.Notification = Notification

    def get_admin_info(self, email):
        admin = self.User.objects.get(email=email)

        return {
            "email": admin.email,
            "first_name": admin.first_name,
        }

    def edit_admin_info(self, email, data):
        admin = self.User.objects.get(email=email)
        serializer = UserSerializer(admin, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return admin

    def get_notification_info(self, user):
        notification_settings = get_object_or_404(self.Notification, user=user)
        return notification_settings

    def update_notification_info(self, user, data):
        notification_settings = get_object_or_404(self.Notification, user=user)
        serializer = NotificationSerializer(notification_settings, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
