from django.conf import settings

from typing import Type
from kink import inject
from openai import OpenAI


from app.models import User


client = OpenAI(
    # default is 2
    max_retries=3,
    api_key=settings.OPENAI_API_KEY
)

@inject
class AuthService:
    def __init__(
        self,
        User: Type[User]):
    
        pass