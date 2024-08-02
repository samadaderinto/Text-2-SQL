from typing import Type
from kink import inject


from app.models import User
@inject
class AuthService:
    def __init__(
        self,
        User: Type[User]):
    
        pass