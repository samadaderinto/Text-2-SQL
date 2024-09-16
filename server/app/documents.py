from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry

from .models import Customer, Notification, Order, Product, Store, User


@registry.register_document
class CustomerDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Customer
        fields = ['name', 'description']


@registry.register_document
class NotificationDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Notification
        fields = ['name', 'description']


@registry.register_document
class OrderDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Order
        fields = ['name', 'description']


@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Product
        fields = ['name', 'description']


@registry.register_document
class StoreDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Store
        fields = ['name', 'description']


@registry.register_document
class UserDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = User
        fields = ['name', 'description']
