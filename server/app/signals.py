from functools import partial

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Customer, Order, Product
from .search_index import delete_instance, index_instance


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Customer)
@receiver(post_save, sender=Order)
def index_searchable_instance(sender, instance, **kwargs):
    if settings.ELASTICSEARCH_ENABLED:
        transaction.on_commit(partial(index_instance, instance), robust=True)


@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=Customer)
@receiver(post_delete, sender=Order)
def delete_searchable_instance(sender, instance, **kwargs):
    if settings.ELASTICSEARCH_ENABLED:
        transaction.on_commit(partial(delete_instance, instance), robust=True)
