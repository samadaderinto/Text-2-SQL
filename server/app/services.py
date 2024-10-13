import json
import re
import secrets
import logging


from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import connection, transaction, IntegrityError
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.apps import apps

from typing import Type
from kink import inject
from openai import OpenAI
from datetime import datetime
from elasticsearch import Elasticsearch

from rest_framework import status
from rest_framework.response import Response


from utils.algorithms import TokenGenerator, auth_token

from .serializers import (
    CustomerSerializer,
    NotificationSerializer,
    ProductSerializer,
    StoreSerializer,
    UserSerializer,
)
from .models import Customer, Notification, Order, Product, Query, Store, User

logger = logging.getLogger(__name__)


@inject
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

    def create_user(self, request, email, password):
        if self.User.objects.filter(email=email).exists():
            return None

        user = self.User.objects.create_user(email=email, password=password)
        self.Store.objects.create(user=user, email=email)
        self.Notification.objects.create(user=user)
        self.send_activation_mail(request, email)

    def login_user(self, request, email, password):
        user = authenticate(request, username=email, password=password)

        if user and user.is_active:
            token = auth_token(user)
            serializer = UserSerializer(user)
            return {"token": token, "data": serializer.data}
        elif user and user.is_active == False:
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

    def reset_password_user(self, request, email, new_password):
        user = get_object_or_404(self.User, email=email)
        user.set_password(new_password)
        user.save()

        return {"success": "Password updated successfully"}


@inject
class StoreService:
    def __init__(self, User: Type[User], Store: Type[Store]):
        self.User = User
        self.Store = Store

    def create_store(self, request, data):
        user = request.user
        store = self.Store.objects.get_or_create(user=user, **data)
        return store

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


@inject
class SearchService:
    def __init__(self, Query: Type[Query]):
        self.Query = Query
        self.commands = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_field_mapping = self.get_all_model_fields()
        self.sensitive_fields = ["password", "token", "secret_key"]
        self.es = Elasticsearch(hosts=[settings.ELASTICSEARCH_DSL["default"]["hosts"]])

    def elastic_search(self, search_query):
        try:
            index_name = "your_index_name"

            query_body = {
                "query": {
                    "multi_match": {
                        "query": search_query,
                        "fields": ["field1", "field2", "field3"],
                    }
                }
            }

            response = self.es.search(index=index_name, body=query_body)

            hits = response.get("hits", {}).get("hits", [])

            result_data = [hit["_source"] for hit in hits]

            return json.dumps(
                {
                    "status": "success",
                    "data": result_data,
                    "message": f"{len(result_data)} results found for query: {search_query}",
                }
            )
        except Exception as e:
            logger.error(f"Error executing Elasticsearch query: {str(e)}")
            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue executing the search query. Please try again later.",
                }
            )

    def custom_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()[:10]
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

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

    def get_all_model_fields(self):
        model_field_mapping = {}
        for model in apps.get_models():
            fields = [field.name for field in model._meta.get_fields()]
            model_field_mapping[model.__name__.lower()] = fields
        # logger.info(f"db tables: {str(model_field_mapping)}")
        return model_field_mapping

    def audio_to_text(self, audio_data):
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_data, response_format="text"
            )
            return response
        except Exception:
            logger.error("Error transcribing audio")
            return None

    def text_to_SQL(self, audio_data):
        text = self.audio_to_text(audio_data)
        model_mappings = self.get_all_model_fields()

        if not text:
            return "Error in audio transcription"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": f"Convert the following text into an SQL query and return the query only, using this model mapping and its respective fields as a guide {model_mappings} in MySQL query format: {text}",
                    }
                ],
                max_tokens=150,
            )

            response_json = response.to_dict()
            parsed_response = self.parse_openai_response(json.dumps(response_json))

            return parsed_response
        except Exception:
            logger.error("Error generating SQL query from OpenAI API")
            return "Error generating SQL query"

    def get_required_fields(self, table_name):
        query = f"""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = '{table_name}' 
        AND IS_NULLABLE = 'NO' 
        AND COLUMN_DEFAULT IS NULL;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            required_fields = [row[0] for row in cursor.fetchall()]

        return required_fields

    def get_incomplete_fields(self, query, required_fields):
        try:
            provided_fields = re.findall(r"\((.*?)\)", query)[0].split(",")
            provided_fields = [field.strip() for field in provided_fields]
            incomplete_fields = [
                field for field in required_fields if field not in provided_fields
            ]

            return incomplete_fields
        except IndexError:
            logger.error("Failed to extract fields from the SQL query.")
            return required_fields

    def fill_defaults_fields(self, query, incomplete_fields):
        if "created" in incomplete_fields:
            fields_part = re.search(r"\((.*?)\)", query).group(1)
            values_part = re.search(r"VALUES\s*\((.*?)\)", query).group(1)

            new_fields_part = fields_part + ", created"
            new_values_part = values_part + ", CURRENT_TIMESTAMP"

            query = query.replace(fields_part, new_fields_part)
            query = query.replace(values_part, new_values_part)

        if "updated" in incomplete_fields:
            fields_part = re.search(r"\((.*?)\)", query).group(1)
            values_part = re.search(r"VALUES\s*\((.*?)\)", query).group(1)

            new_fields_part = fields_part + ", updated"
            new_values_part = values_part + ", CURRENT_TIMESTAMP"

            query = query.replace(fields_part, new_fields_part)
            query = query.replace(values_part, new_values_part)

        if "is_active" in incomplete_fields:
            fields_part = re.search(r"\((.*?)\)", query).group(1)
            values_part = re.search(r"VALUES\s*\((.*?)\)", query).group(1)

            new_fields_part = fields_part + ", is_active"
            new_values_part = values_part + ", TRUE"

            query = query.replace(fields_part, new_fields_part)
            query = query.replace(values_part, new_values_part)

        return query

    def extract_update_fields_and_values(self, query):
        try:
            match = re.search(
                r"UPDATE\s+\w+\s+SET\s+(.+?)\s+WHERE", query, re.IGNORECASE
            )
            if not match:
                return None

            set_clause = match.group(1)

            field_value_pairs = set_clause.split(",")

            update_data = {}
            for pair in field_value_pairs:
                field, value = pair.split("=")
                update_data[field.strip()] = value.strip().strip("'\"")

            return update_data

        except Exception as e:
            logger.error(f"Error extracting fields and values from query: {str(e)}")
            return None

    def extract_insert_fields_and_values_from_query(self, query):
        match = re.search(
            r"INSERT\s+INTO\s+[`'\"]?(\w+)[`'\"]?\s*\(([^)]+)\)\s+VALUES\s*\(([^)]+)\)",
            query,
            re.IGNORECASE,
        )
        if match:
            fields_str = match.group(2)
            values_str = match.group(3)

            fields = [field.strip() for field in fields_str.split(",")]
            values = [value.strip() for value in values_str.split(",")]

            return dict(zip(fields, values))

        return {}

    def send_create_incompleted_response(self, table_name, query):
        required_fields = self.get_required_fields(table_name)

        provided_fields = self.extract_insert_fields_and_values_from_query(query)
        incomplete_fields = [field for field in required_fields if field not in provided_fields.keys()]

        all_fields = {field: provided_fields.get(field, "") for field in required_fields}

        return {
            "completed_fields": {field: value for field, value in all_fields.items() if value},
            "incomplete_fields": {field: "" for field in incomplete_fields},
        }


    @transaction.atomic
    def confirm_and_execute_update(self, validated_data):
        query = self.Query.objects.last()

        try:
            if validated_data:
                modified_query = query.query.format(**validated_data)

                query.query = modified_query
                query.save()

            with connection.cursor() as cursor:
                cursor.execute(query.query)

            query.delete()

            return json.dumps(
                {
                    "status": "success",
                    "message": "The update query was successfully executed.",
                }
            )

        except Exception as e:
            logger.error(f"Error executing SQL update query after validation: {str(e)}")

            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue executing the update query after validation. Please try again later.",
                }
            )

    @transaction.atomic
    def confirm_and_execute_delete(self):
        query = self.Query.objects.last()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query.query)

            query.delete()
            return json.dumps(
                {
                    "status": "success",
                    "message": "The delete query was successfully executed.",
                }
            )

        except Exception as e:
            logger.error(f"Error executing SQL delete query after validation: {str(e)}")
            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue executing the delete query after validation. Please try again later.",
                }
            )

    @transaction.atomic
    def confirm_and_execute_create(self, validated_data):

        query = self.Query.objects.last()

        if validated_data:
            modified_query = query.query.format(**validated_data)
            query.query = modified_query
            query.save()

        match = re.search(
            r"INSERT\s+INTO\s+[`'\"]?(\w+)[`'\"]?\s*\(", query.query, re.IGNORECASE
        )
        table_name = match.group(1) if match else None

        if not table_name:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Table name could not be identified in the query.",
                }
            )

        required_fields = self.get_required_fields(table_name)

        incomplete_fields = self.get_incomplete_fields(query.query, required_fields)

        if incomplete_fields:
            query.query = self.fill_defaults_fields(query.query, incomplete_fields)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query.query)
            query.delete()

            return json.dumps(
                {
                    "status": "success",
                    "message": "The create query was successfully executed.",
                }
            )

        except Exception as e:
            logger.error(f"Error executing SQL create query: {str(e)}")
            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue executing the create query. Please try again later.",
                }
            )

    @transaction.atomic()
    def create_from_SQL(self, query):
        try:
            match = re.search(r"INSERT\s+INTO\s+([`'\"]?)(\w+)\1", query, re.IGNORECASE)
            table_name = match.group(2) if match else "Unknown table"

            fields_and_values = self.extract_insert_fields_and_values_from_query(query)
            incomplete_fields = self.get_incomplete_fields(query, fields_and_values.keys())

            if incomplete_fields:
                response_data = self.send_create_incompleted_response(table_name, query)
                return json.dumps({
                    "status": "pending_validation",
                    "message": f"Please verify the fields for {table_name}.",
                    "fields": response_data
                })

            self.Query.objects.create(query=query)

            return json.dumps({
                "status": "success",
                "message": "Successfully executed and added."
            })

        except IntegrityError as e:
            logger.error(f"IntegrityError executing SQL insert query: {str(e)}")
            incomplete_fields = self.send_create_incompleted_response(table_name, query)

            return json.dumps({
                "status": "error",
                "message": "There was an issue with the data integrity. Please ensure all required fields are provided.",
                "fields": incomplete_fields,
            })

        except Exception as e:
            logger.error(f"Error executing SQL insert query: {str(e)}")
            return json.dumps({
                "status": "error",
                "message": "There was an issue executing the insert query. Please try again later.",
            })

    @transaction.atomic()
    def update_from_SQL(self, query):
        try:
            match = re.search(r"UPDATE\s+([`'\"]?)(\w+)\1", query, re.IGNORECASE)
            table_name = match.group(2) if match else "Unknown table"

            fields_and_values = self.extract_update_fields_and_values(query)
            if fields_and_values:
                self.Query.objects.create(query=query)
                return json.dumps(
                    {
                        "status": "pending_validation",
                        "message": f"Please validate the following fields for {table_name}.",
                        "fields": fields_and_values,
                    }
                )
            else:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Unable to extract update fields and values from the query.",
                    }
                )

        except Exception as e:
            logger.error(f"Error executing SQL update query in update: {str(e)}")
            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue executing the update query. Please try again later.",
                }
            )

    def get_from_SQL(self, query):
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()

                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in data]

                filtered_result = self.filter_sensitive_data(result)
                return json.dumps(filtered_result, default=self.custom_serializer)

        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            return "There was an issue executing the SQL query. Please try again later."

    @transaction.atomic
    def delete_from_SQL(self, audio_data):
        query = self.text_to_SQL(audio_data)

        try:
            match = re.search(
                r"DELETE\s+FROM\s+([`'\"]?)(\w+)\1\s+WHERE\s+(.+)", query, re.IGNORECASE
            )
            table_name = match.group(2) if match else "Unknown table"
            condition = match.group(3) if match else "Unknown condition"

            if table_name and condition:
                return json.dumps(
                    {
                        "status": "pending_validation",
                        "message": f"Please confirm the deletion from {table_name} where {condition}.",
                        "fields": {"table": table_name, "condition": condition},
                    }
                )
            else:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Unable to extract table name or condition from the DELETE query.",
                    }
                )

        except Exception as e:
            logger.error(f"Error preparing SQL delete query: {str(e)}")
            return json.dumps(
                {
                    "status": "error",
                    "message": "There was an issue preparing the delete query. Please try again later.",
                }
            )

    def run_SQL_query(self, audio_data):
        query = self.text_to_SQL(audio_data)

        if self.commands[0] in query and query:
            return (self.get_from_SQL(query), self.commands[0])
        elif self.commands[1] in query and query:
            return (self.create_from_SQL(query), self.commands[1])
        elif self.commands[2] in query and query:
            return (self.update_from_SQL(query), self.commands[2])
        elif self.commands[3] in query and query:
            return (self.delete_from_SQL(query), self.commands[3])
        else:
            raise ValueError(
                query, "Invalid SQL command. Please provide a valid SQL command."
            )

    def filter_sensitive_data(self, result):
        for row in result:
            for field in self.sensitive_fields:
                if field in row:
                    del row[field]
        return result

    def extract_fields_from_query(self, query):
        match = re.search(
            r"INSERT\s+INTO\s+[`'\"]?(\w+)[`'\"]?\s*\(([^)]+)\)", query, re.IGNORECASE
        )
        if match:
            field_str = match.group(2)  # Extract the field names within parentheses
            fields = [field.strip() for field in field_str.split(",")]
            return fields
        return []


@inject
class ProductService:
    def __init__(self, User: Type[User], Product: Type[Product]):
        self.User = User
        self.Product = Product

    def get_products(self):
        product = get_object_or_404(self.Product)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_product(self, product_id):
        product = get_object_or_404(self.Product, pk=product_id)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)

    def create_product(self, serializer):
        serializer.save()
        return serializer.data

    def update_product(self, data):
        store = data["store"]
        product_id = data["id"]
        product = get_object_or_404(self.Product, store=store, pk=product_id)
        serializer = ProductSerializer(product, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


@inject
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

    def create_customer(self, serializer):
        customer, created = self.Customer.objects.get_or_create(**serializer.data)
        if not created:
            return None
        return CustomerSerializer(customer)

    def update_customer(self, data):
        email = data["email"]
        phone_number = data["phone_number"]
        customer = get_object_or_404(
            self.Customer, email=email, phone_number=phone_number
        )
        serializer = CustomerSerializer(customer, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


@inject
class OrderService:
    def __init__(self, User: Type[User], Order: Type[Order]):
        self.User = User
        self.Order = Order

    def get_orders(self, user):
        order = get_list_or_404(self.Order, user=user)
        return order

    def create_order(self, serializer):
        serializer.save()
        return serializer.data

    def update_order(self, data):
        id = data["id"]
        user_id = data["user_id"]
        order = get_object_or_404(self.Order, id=id, user__id=user_id)
        serializer = CustomerSerializer(order, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


@inject
class SettingsService:
    def __init__(self, User: Type[User], Notification: Type[Notification]):
        self.User = User
        self.Notification = Notification

    def get_admin_info(self, email):
        admin = self.User.objects.get(email=email)

        return {
            "email": admin.email,
            "first_name": admin.first_name,
            "password": secrets.token_hex(16),
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
        serializer = NotificationSerializer(notification_settings, data)
        return serializer
