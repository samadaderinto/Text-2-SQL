from typing import Type
from kink import di
from app.models import User, Store, Product


di[Type[User]] = User
di[Type[Store]] = Store
di[Type[Product]] = Product