from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch

from app.models import Customer, Order, Product
from app.search_index import (
    SEARCH_DEFINITIONS,
    bulk_index_instances,
    ensure_search_indices,
)


class Command(BaseCommand):
    help = "Create Elasticsearch search indices and index existing products, customers, and orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="Delete and recreate the search indices before indexing.",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        client_options = {"request_timeout": 10}
        if settings.ELASTICSEARCH_USER and settings.ELASTICSEARCH_PASSWORD:
            client_options["basic_auth"] = (
                settings.ELASTICSEARCH_USER,
                settings.ELASTICSEARCH_PASSWORD,
            )
        client = Elasticsearch(settings.ELASTICSEARCH_URL, **client_options)

        try:
            if options["rebuild"]:
                for definition in SEARCH_DEFINITIONS.values():
                    index = definition["index"]
                    if client.indices.exists(index=index):
                        client.indices.delete(index=index)
            ensure_search_indices(client)
            counts = []
            for resource, definition in SEARCH_DEFINITIONS.items():
                queryset = definition["model"].objects.all().iterator(chunk_size=500)
                _, indexed = bulk_index_instances(client, queryset)
                counts.append(f"{resource}: {indexed}")
        finally:
            client.close()

        self.stdout.write(self.style.SUCCESS(f"Search indices ready ({', '.join(counts)})."))
