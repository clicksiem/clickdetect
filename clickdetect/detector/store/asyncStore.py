from asyncio import Lock
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from .datastore import BaseDataStore


class AsyncStore(BaseDataStore):
    """In-process store used when Redis isn't configured.

    Single-replica only: the lock is a local ``asyncio.Lock`` and the window
    state lives in memory, so it is lost on restart. Behaves like the previous
    in-instance scheduling state.
    """

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self._lock = Lock()
        self._last_time: float = 0.0

    @asynccontextmanager
    async def lock(self) -> AsyncGenerator[bool]:
        async with self._lock:
            yield True

    async def get_last_time(self) -> float:
        return self._last_time

    async def set_last_time(self, ts: float) -> None:
        self._last_time = ts
