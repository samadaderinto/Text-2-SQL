from django.contrib import admin
from .models import (
    Notification,
    User,
    Store,
    Product,
    Cart,
    CartItem,
    Order,
    Customer,
    Query,
)

# Register your models here.
admin.site.register(User)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(Notification)
admin.site.register(Query)
