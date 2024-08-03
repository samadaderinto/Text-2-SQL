from django.conf import settings

from typing import Type
from kink import inject
from openai import OpenAI


from .models import User




@inject
class AuthService:
    def __init__(
        self,
        User: Type[User]):
    
        pass
    
    
    
    
client = OpenAI(
    # default max_retries is 2
    max_retries=3,
    api_key=settings.OPENAI_API_KEY
)
@inject
class QueryService:
    def __init__(
        self,
        User: Type[User]):
    
        pass
    
    def audio_to_text(self, request):
        pass
    
    def text_to_SQL(self, request):
        pass
    
    def runSQLQuery(self, request):
        pass
    

@inject
class ProductService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass
    
    
    def products(self):
        pass
        
  

@inject
class CustomerService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass
  
  
@inject
class OrderService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass
  
  
@inject
class SettingsService:
    def __init__(
        self,
        User: Type[User]
    ):
        
      pass