from asyncio import CancelledError, create_task, sleep
from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from .datastore import BaseDataStore

logger = getLogger(__name__)


class RedisStore(BaseDataStore):
    """Redis-backed store for high-availability, multi-replica deployments.

    The per-detector lock is a distributed, non-blocking lock: only one replica
    acquires it for a given detector run; the others skip. The window state
    (``last_time``) is shared, so a replica taking over after a failover resumes
    from the exact same window with no gap or reprocessing.
    """

    def __init__(
        self,
        key: str,
        url: str = "",
        namespace: str = "clickdetect",
        lock_ttl: int = 1500,
    ) -> None:
        super().__init__(key)
        if not url:
            raise ValueError('Invalid url')
        if lock_ttl <= 0:
            raise ValueError('Invalid lock_ttl, min is 1')

        self._url = url
        self._namespace = namespace
        self._lock_ttl = lock_ttl
        self._redis: Redis | None = None

    @property
    def _win_key(self) -> str:
        return f"{self._namespace}:win:{self.key}"

    @property
    def _lock_key(self) -> str:
        return f"{self._namespace}:lock:{self.key}"

    async def connect(self) -> None:
        self._redis = Redis.from_url(self._url, decode_responses=True)
        await self._redis.ping()
        logger.info(f"RedisStore connected | key: {self.key}")

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()

    @asynccontextmanager
    async def lock(self) -> AsyncGenerator[bool]:
        if self._redis is None:
            raise RuntimeError("RedisStore.connect() was not called")

        redis_lock = self._redis.lock(
            self._lock_key, timeout=self._lock_ttl, blocking=False
        )
        acquired = await redis_lock.acquire()
        watchdog = create_task(self._renew_lock(redis_lock)) if acquired else None
        try:
            yield acquired
        finally:
            if watchdog is not None:
                watchdog.cancel()
                try:
                    await watchdog
                except CancelledError:
                    pass
            if acquired:
                try:
                    await redis_lock.release()
                except Exception as ex:
                    logger.warning(f"Could not release lock {self._lock_key}: {ex}")

    async def _renew_lock(self, redis_lock: Lock) -> None:
        interval = max(self._lock_ttl / 3, 1)
        while True:
            await sleep(interval)
            try:
                await redis_lock.extend(self._lock_ttl, replace_ttl=True)
            except Exception as ex:
                logger.warning(
                    f"Lock watchdog could not extend {self._lock_key}: {ex}"
                )
                return

    async def get_last_time(self) -> float:
        if self._redis is None:
            raise RuntimeError("RedisStore.connect() was not called")
        val = await self._redis.get(self._win_key)
        return float(val) if val is not None else 0.0

    async def set_last_time(self, ts: float) -> None:
        if self._redis is None:
            raise RuntimeError("RedisStore.connect() was not called")
        await self._redis.set(self._win_key, ts)
