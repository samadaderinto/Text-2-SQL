from typing import Type
from kink import di


from .models import User, Store, Product, Cart, CartItem, Order


di[Type[User]] = User
di[Type[Store]] = Store
di[Type[Product]] = Product
di[Type[Cart]] = Cart
di[Type[CartItem]] = CartItem
di[Type[Order]] = Order