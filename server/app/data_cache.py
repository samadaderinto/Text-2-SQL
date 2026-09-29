import hashlib
import json

from django.core.cache import cache


def make_data_cache_key(namespace, value):
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"audql:data:{namespace}:{digest}"


def get_data_cache_version(resources):
    return {
        resource: cache.get(f"audql:data:version:{resource}", 0)
        for resource in sorted(resources)
    }


def invalidate_data_cache(resource):
    version_key = f"audql:data:version:{resource}"
    cache.add(version_key, 0, timeout=None)
    cache.incr(version_key)
