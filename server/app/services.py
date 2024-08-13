import os

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.db import connection
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from typing import Type
from kink import inject
from openai import OpenAI, Audio
from pydub import AudioSegment

from rest_framework import status
from rest_framework.response import Response

from utils.algorithms import TokenGenerator, auth_token, send_email, send_mail

from .serializers import CustomerSerializer, ProductSerializer, UserSerializer
from .models import Customer, Product, User



@inject
class AuthService:
    def __init__(self, User: Type[User]):
        self.User = User
        
    def get_base_url(self, request):
        scheme = request.scheme  # 'http' or 'https'
        host = request.get_host()  # 'example.com' or 'example.com:8000'
        return f'{scheme}://{host}'


    def send_activation_mail(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = TokenGenerator().make_token(user)
        link = f'{self.get_base_url(request)}/auth/activate/{uidb64}/{token}/'
        absolute_url = request.build_absolute_uri(link)
        # send_mail(
        #     'onboarding-user',
        #     user.email,
        #     data={'firstname': user.first_name, 'absolute_url': absolute_url}
        # )
        
        send_email(
            
         absolute_url
        )

    
    def create_user(self, request, email, password):
        if self.User.objects.filter(email=email).exists():
            return None  

        self.User.objects.create_user(email=email, password=password)
        self.send_activation_mail(request, email)

    
    def login_user(self, request, email, password):
        user = authenticate(request, username=email, password=password)
      
        if user and user.is_active:
            token = auth_token(user)
            serializer = UserSerializer(user)
            return {'token': token, 'data': serializer.data}
        elif user and not user.is_active:
            return {"verify": "Please verify your email account"}
        return {"invalid_info": "Invalid user information"}
    
    def request_reset_password_user(self, request, email):
        user = get_object_or_404(self.User, email=email)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f'{self.get_base_url(request)}/auth/reset-password/verify/{uidb64}/{token}/'
        
        return request.build_absolute_uri(link)
    
    def reset_password_user(self, request, email, new_password):
        user = get_object_or_404(self.User, email=email)
        user.set_password(new_password)
        user.save()
        
        return {'success': "Password updated successfully"}
        
      
        

client = OpenAI(
    # default max_retries is 2
    max_retries=3,
    api_key=settings.OPENAI_API_KEY
)


@inject
class QueryService:
    def __init__(self):
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

        return response['text']
       

    def text_to_SQL(self, request, wav_file_path, file_path):
        text = self.audio_to_text(request, wav_file_path, file_path)
        
        return text

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
    def __init__(self, User: Type[User], Customer: Type[Customer]):
        self.User = User
        self.Customer = Customer

    def get_customers(self, data):
        pass

    def get_customer(self, request, email, phone):
     
        customer = get_object_or_404(Customer, email=email, phone=phone)
        
        return customer

    def create_customer(self, request, serializer):
        serializer.save()
        return serializer.data
       

    def update_customer(self, data):
        email = data["email"]
        phone = data["phone"]
      
        customer = get_object_or_404(Customer, email=email, phone=phone)
        serializer = CustomerSerializer(customer, data=data)
        serializer.is_valid(raise_exceptions=True)
        serializer.save()
        return serializer.data


@inject
class OrderService:
    def __init__(self, User: Type[User], Product: Type[Product]):
        self.User = User,
        self.Product = Product
        

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
        self.User = User
