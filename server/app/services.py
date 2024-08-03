from django.conf import settings

from typing import Type
from kink import inject
from openai import OpenAI


from app.models import User




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