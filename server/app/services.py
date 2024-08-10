import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.db import connection
from django.core.files.storage import default_storage

from typing import Type
from kink import inject
from openai import OpenAI, Audio
from pydub import AudioSegment

from rest_framework import status
from rest_framework.response import Response

from utils.algorithms import TokenGenerator, auth_token, send_mail

from .serializers import ProductSerializer, UserSerializer
from .models import Product, User



@inject
class AuthService:
    def __init__(self, User: Type[User]):
        self.User = User

    def send_activation_mail(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uuidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = TokenGenerator().make_token(user)
        current_site = get_current_site(request).domain
        relativeLink = reverse('activate', kwargs={'uidb64': uuidb64, 'token': token})
        absolute_url = f"http://{current_site}{relativeLink}"
        send_mail(
            'onboarding-user',
            user.email,
            data={'firstname': user.first_name, 'absolute_url': absolute_url}
        )

    
    def create_user(self, request, data):
        email = data['email']

        if self.User.objects.filter(email=email).exists():
            return None  

        self.User.objects.create_user(**data)
        self.send_activation_mail(request, email)

    
    def login(self, request, data):
        user = get_object_or_404(self.User, email=data['email'])
        token = auth_token(user)
        user_serializer = UserSerializer(user)
        return {'token': token, 'data': user_serializer.data}
       


 


client = OpenAI(
    # default max_retries is 2
    max_retries=3,
    api_key=settings.OPENAI_API_KEY
)


@inject
class QueryService:
    def __init__(self, User: Type[User]):
        self.User = User
        self.commands = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']

    def sanitize_sql_query(self, query):
        query = query.strip()
        # Extract the command (first word) from the query
        command = query.split(' ', 1)[0].upper()

        if command in self.commands:
            # Perform basic sanitization
            # This should be extended with more thorough checks for a production environment
            return query
        else:
            raise ValueError('Disallowed SQL command')

    def audio_to_text(self, request, wav_file_path, file_path):
        

        with open(wav_file_path, 'rb') as f:
            response = Audio.transcribe(model='whisper-1', file=f)

        os.remove(file_path)
        os.remove(wav_file_path)

        return response['text']
       

    def text_to_SQL(self, request, wav_file_path, file_path):
        text = self.audio_to_text(request, wav_file_path, file_path)

    def runSQLQuery(self, request, wav_file_path, file_path):
        query = self.text_to_SQL(request, wav_file_path, file_path)
        sanitized_query = self.sanitize_query(query)
        with connection.cursor() as cursor:
            cursor.execute(sanitized_query)
            data = cursor.fetchall()
        return data


@inject
class ProductService:
    def __init__(self, User: Type[User], Product: Type[Product]):
        self.User = User
        self.Product = Product

    def get_products(self, product_id):
        product = get_object_or_404(self.Product, id=product_id)
        serializer = ProductSerializer(product)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_product(self, product_id):
        product = get_object_or_404(self.Product, id=product_id)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)

    def create_product(self):
        pass

    def update_product(self):
        pass


@inject
class CustomerService:
    def __init__(self, User: Type[User]):
        pass

    def get_customers(self):
        pass

    def get_customer(self):
        pass

    def ban_customer(self):
        pass

    def create_product(self):
        pass

    def update_product(self):
        pass


@inject
class OrderService:
    def __init__(self, User: Type[User]):
        pass

    def create_product(self):
        pass

    def update_product(self):
        pass

    def get_customers(self):
        pass

    def get_customer(self):
        pass


@inject
class SettingsService:
    def __init__(self, User: Type[User]):
        pass
