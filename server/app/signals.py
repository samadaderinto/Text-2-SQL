from functools import partial

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .data_cache import invalidate_data_cache
from .job_queue import enqueue_job
from .models import Customer, Order, Product, QueueJob


RESOURCE_BY_MODEL = {
    Product: "products",
    Customer: "customers",
    Order: "orders",
}


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Customer)
@receiver(post_save, sender=Order)
def index_searchable_instance(sender, instance, **kwargs):
    transaction.on_commit(
        partial(invalidate_data_cache, RESOURCE_BY_MODEL[sender]), robust=True
    )
    if settings.ELASTICSEARCH_ENABLED:
        enqueue_job(
            QueueJob.Kind.SEARCH_INDEX,
            {
                "resource": RESOURCE_BY_MODEL[sender],
                "record_id": str(instance.pk),
            },
        )


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=Customer)
@receiver(post_delete, sender=Order)
def delete_searchable_instance(sender, instance, **kwargs):
    transaction.on_commit(
        partial(invalidate_data_cache, RESOURCE_BY_MODEL[sender]), robust=True
    )
    if settings.ELASTICSEARCH_ENABLED:
        enqueue_job(
            QueueJob.Kind.SEARCH_DELETE,
            {
                "resource": RESOURCE_BY_MODEL[sender],
                "record_id": str(instance.pk),
            },
        )
