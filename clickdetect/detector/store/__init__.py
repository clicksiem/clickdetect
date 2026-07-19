from typing import Any, Dict

from .asyncStore import AsyncStore
from .datastore import BaseDataStore
from .redisStore import RedisStore

__all__ = ["BaseDataStore", "AsyncStore", "RedisStore", "create_store"]


def create_store(key: str, redis_config: Dict[str, Any] | None) -> BaseDataStore:
    if redis_config:
        return RedisStore(key, **redis_config)
    return AsyncStore(key)
