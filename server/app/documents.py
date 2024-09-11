from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry

from .models import Customer, Notification, Order, Product, Store, User


@registry.register_document
class CustomerDocument(Document):
    pass

@registry.register_document
class Notification(Document):
    pass

@registry.register_document
class OrderDocument(Document):
    pass

@registry.register_document
class ProductDocument(Document):
    pass

@registry.register_document
class StoreDocument(Document):
    pass

@registry.register_document
class UserDocument(Document):
    pass