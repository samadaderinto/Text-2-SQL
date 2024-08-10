from typing import Type
from kink import di


from .models import User, Store, Product, Cart, CartItem, Order


di[User] = User
di[Store] = Store
di[Product] = Product
di[Cart] = Cart
di[CartItem] = CartItem
di[Order] = Order