from functools import lru_cache

from django.conf import settings
from elasticsearch import Elasticsearch, helpers

from .models import Customer, Order, Product


SEARCH_DEFINITIONS = {
    "products": {
        "index": "audql-products",
        "model": Product,
        "properties": {
            "entity_id": {"type": "keyword"},
            "owner_id": {"type": "keyword"},
            "search_text": {"type": "text"},
            "created": {"type": "date"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "category": {"type": "keyword"},
            "available": {"type": "integer"},
            "price": {"type": "double"},
        },
    },
    "customers": {
        "index": "audql-customers",
        "model": Customer,
        "properties": {
            "entity_id": {"type": "keyword"},
            "owner_id": {"type": "keyword"},
            "search_text": {"type": "text"},
            "created": {"type": "date"},
        },
    },
    "orders": {
        "index": "audql-orders",
        "model": Order,
        "properties": {
            "entity_id": {"type": "keyword"},
            "owner_id": {"type": "keyword"},
            "search_text": {"type": "text"},
            "created": {"type": "date"},
            "status": {"type": "keyword"},
            "total": {"type": "double"},
            "subtotal": {"type": "double"},
        },
    },
}


@lru_cache(maxsize=1)
def get_elasticsearch_client():
    options = {"request_timeout": 5}
    if settings.ELASTICSEARCH_USER and settings.ELASTICSEARCH_PASSWORD:
        options["basic_auth"] = (
            settings.ELASTICSEARCH_USER,
            settings.ELASTICSEARCH_PASSWORD,
        )
    return Elasticsearch(settings.ELASTICSEARCH_URL, **options)


def ensure_search_indices(client, resources=None):
    resources = resources or SEARCH_DEFINITIONS.keys()
    for resource in resources:
        definition = SEARCH_DEFINITIONS[resource]
        index = definition["index"]
        if not client.indices.exists(index=index):
            client.indices.create(
                index=index,
                mappings={"properties": definition["properties"]},
                settings={"number_of_shards": 1, "number_of_replicas": 0},
            )


def document_for_instance(instance):
    if isinstance(instance, Product):
        resource = "products"
        owner_id = instance.store.user_id
        search_fields = (instance.title, instance.description, instance.category)
        extra_fields = {
            "title": instance.title,
            "description": instance.description,
            "category": instance.category,
            "available": instance.available,
            "price": float(instance.price),
        }
    elif isinstance(instance, Customer):
        resource = "customers"
        owner_id = instance.user_id
        search_fields = (
            instance.first_name,
            instance.last_name,
            instance.email,
            instance.phone_number,
        )
        extra_fields = {}
    elif isinstance(instance, Order):
        resource = "orders"
        owner_id = instance.user_id
        search_fields = (instance.id, instance.status)
        extra_fields = {
            "status": instance.status,
            "total": float(instance.total),
            "subtotal": float(instance.subtotal),
        }
    else:
        raise TypeError(f"Unsupported search document model: {type(instance).__name__}")

    return resource, {
        "entity_id": str(instance.pk),
        "owner_id": str(owner_id),
        "search_text": " ".join(str(value) for value in search_fields if value),
        "created": instance.created.isoformat(),
        **extra_fields,
    }


def index_instance(instance):
    resource, document = document_for_instance(instance)
    client = get_elasticsearch_client()
    ensure_search_indices(client, [resource])
    client.index(
        index=SEARCH_DEFINITIONS[resource]["index"],
        id=str(instance.pk),
        document=document,
    )


def delete_instance(instance):
    if isinstance(instance, Product):
        resource = "products"
    elif isinstance(instance, Customer):
        resource = "customers"
    elif isinstance(instance, Order):
        resource = "orders"
    else:
        raise TypeError(f"Unsupported search document model: {type(instance).__name__}")
    client = get_elasticsearch_client()
    index = SEARCH_DEFINITIONS[resource]["index"]
    if client.indices.exists(index=index):
        client.options(ignore_status=404).delete(index=index, id=str(instance.pk))


def bulk_index_instances(client, instances):
    def actions():
        for instance in instances:
            resource, document = document_for_instance(instance)
            yield {
                "_op_type": "index",
                "_index": SEARCH_DEFINITIONS[resource]["index"],
                "_id": str(instance.pk),
                "_source": document,
            }

    return helpers.bulk(client, actions(), refresh="wait_for")
