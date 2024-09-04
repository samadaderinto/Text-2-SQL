import json
import secrets
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import connection
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.apps import apps

from typing import Type
from kink import inject
from openai import OpenAI

from rest_framework import status
from rest_framework.response import Response


from utils.algorithms import TokenGenerator, auth_token

from .serializers import (
    CustomerSerializer,
    NotificationSerializer,
    ProductSerializer,
    StoreSerializer,
    UserSerializer
)
from .models import Customer, Notification, Order, Product, Store, User

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
        return f'{scheme}://{host}'

    def send_activation_mail(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = TokenGenerator().make_token(user)
        link = f'{self.get_base_url(request)}/auth/activate/{uidb64}/{token}/'
        absolute_url = request.build_absolute_uri(link)

        send_mail(
            f'Welcome, {email}',
            f"This is the link to verify your email. {absolute_url}",
            'adesamad1234@gmail.com',
            [email],
            fail_silently=False
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
            return {'token': token, 'data': serializer.data}
        elif user and user.is_active == False:
            return {'verify': 'Please verify your email account'}

        return {'invalid_info': 'Invalid user information'}

    def request_reset_password_user(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = (
            f'{self.get_base_url(request)}/auth/reset-password/verify/{uidb64}/{token}/'
        )

        return request.build_absolute_uri(link)

    def reset_password_user(self, request, email, new_password):
        user = get_object_or_404(self.User, email=email)
        user.set_password(new_password)
        user.save()

        return {'success': 'Password updated successfully'}


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
        return {'success': 'Store deleted successfully'}

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
class QueryService:
    def __init__(self):
        self.commands = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_field_mapping = self.get_all_model_fields()

    def parse_openai_response(self, response_json):
        try:
            response = json.loads(response_json)
            if (
                'choices' in response
                and response['choices'][0]['finish_reason'] == 'stop'
            ):
                message_content = response['choices'][0]['message']['content']
                message_content = message_content.strip().strip('```').strip()

                if 'Could you please provide more context or detail' in message_content:
                    return 'The assistant needs more context or detail to generate the SQL query.'
                return message_content

            else:
                return 'The response was incomplete or there was an issue.'

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return 'Error parsing the response from OpenAI.'

        except KeyError as e:
            logger.error(f"Missing key in response: {str(e)}")
            return 'Error processing the response from OpenAI.'

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return 'Unexpected error processing the response.'

    def get_all_model_fields(self):
        model_field_mapping = {}

        for model in apps.get_models():
            fields = [field.name for field in model._meta.get_fields()]
            model_field_mapping[model.__name__.lower()] = fields
        return model_field_mapping

    def audio_to_text(self, request, audio_data):
        response = self.client.audio.transcriptions.create(
            model='whisper-1', file=audio_data, response_format='text'
        )
        return response

    def text_to_SQL(self, request, audio_data):
        text = self.audio_to_text(request, audio_data)
        model_mappings = self.get_all_model_fields()
        if not text:
            return 'Error in audio transcription'

        try:
            response = self.client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {
                        'role': 'user',
                        'content': f"Convert the following text into an SQL query and return the query only, using this model mapping and its respective field has a guide {model_mappings}: {text}"
                    }
                ],
                max_tokens=150
            )

            response_json = response.to_dict()

            parsed_response = self.parse_openai_response(json.dumps(response_json))

            return parsed_response

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return 'Error generating SQL query'

    def run_SQL_query(self, request, audio_data):
        query = self.text_to_SQL(request, audio_data)

        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        return data, query


@inject
class ProductService:
    def __init__(self, User: Type[User], Product: Type[Product]):
        self.User = User
        self.Product = Product

    def get_products(self, data):
        store = data['store']
        product_id = data['id']
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
        store = data['store']
        product_id = data['id']
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
        email = data['email']
        phone_number = data['phone_number']
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
        id = data['id']
        user_id = data['user_id']
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
            'email': admin.email,
            'first_name': admin.first_name,
            'password': secrets.token_hex(16)
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
