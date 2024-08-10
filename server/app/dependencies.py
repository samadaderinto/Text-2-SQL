from kink import di
from .services import AuthService, CustomerService, OrderService, ProductService, QueryService, SettingsService
from .models import User, Store, Product, Cart, CartItem, Order





def di_setup():
   

    di[User] = User
    di[Store] = Store
    di[Product] = Product
    di[Cart] = Cart
    di[CartItem] = CartItem
    di[Order] = Order


    di[AuthService] = AuthService(di[User])
    di[ProductService] = ProductService(di[User], di[Product])
    di[OrderService] = OrderService(di[User], di[Product])
    di[CustomerService] = CustomerService(di[User])
    di[QueryService] = QueryService()
    di[SettingsService] = SettingsService(di[User])
