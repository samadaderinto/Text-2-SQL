from kink import di
from .services import AuthService, CustomerService, OrderService, ProductService, QueryService, SettingsService
from .models import User, Store, Product, Cart, CartItem, Order, Customer



def di_setup():
   
    di[User] = User
    di[Store] = Store
    di[Product] = Product
    di[Cart] = Cart
    di[CartItem] = CartItem
    di[Order] = Order
    di[Customer] = Customer

    di[AuthService] = AuthService(di[User])
    di[ProductService] = ProductService(di[User], di[Product])
    di[OrderService] = OrderService(di[User], di[Order])
    di[CustomerService] = CustomerService(di[User], di[Customer])
    di[QueryService] = QueryService()
    di[SettingsService] = SettingsService(di[User])
