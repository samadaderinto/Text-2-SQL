from kink import di
from .services import (
    AuthService,
    CustomerService,
    OrderService,
    ProductService,
    SearchService,
    SettingsService,
    StoreService
)
from .models import Notification, User, Store, Product, Cart, CartItem, Order, Customer


def di_setup():
    di[User] = User
    di[Store] = Store
    di[Product] = Product
    di[Cart] = Cart
    di[CartItem] = CartItem
    di[Order] = Order
    di[Customer] = Customer
    di[Store] = Store
    di[Notification] = Notification

    di[AuthService] = AuthService(di[User], di[Store], di[Notification])
    di[ProductService] = ProductService(di[User], di[Product])
    di[OrderService] = OrderService(di[User], di[Order])
    di[CustomerService] = CustomerService(di[User], di[Customer])
    di[SearchService] = SearchService()
    di[StoreService] = StoreService(di[User], di[Store])
    di[SettingsService] = SettingsService(di[User], di[Notification])
