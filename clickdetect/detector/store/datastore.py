from contextlib import AbstractAsyncContextManager


class BaseDataStore:
    """Abstract state store for detector scheduling.

    Holds the per-detector detection window (``last_time``) and provides a
    ``lock`` that guarantees a single execution of a given detector run.

    In a single process the lock is local (see :class:`AsyncStore`); backed by
    Redis it becomes a distributed lock so multiple replicas never run the same
    detector window twice. Because the lock and the window state are shared,
    no separate leader election is needed for high availability.
    """

    def __init__(self, key: str) -> None:
        self.key = key

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass

    def lock(self) -> AbstractAsyncContextManager[bool]:
        """Return an async context manager yielding whether the lock was held.

        Usage::

            async with store.lock() as acquired:
                if not acquired:
                    return
                ...
        """
        raise NotImplementedError

    async def get_last_time(self) -> float:
        raise NotImplementedError

    async def set_last_time(self, ts: float) -> None:
        raise NotImplementedError
