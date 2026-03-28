from typing import List
from logging import getLogger
import asyncpg

from ..utils import Parameters
from .base import BaseDataSource, DataSourceQueryResult

logger = getLogger(__name__)


class PostgreSQLDataSource(BaseDataSource):
    database: str
    host: str
    port: int
    username: str
    password: str
    _pool: asyncpg.Pool | None = None

    async def connect(self):
        try:
            self._pool = await asyncpg.create_pool(
                database=self.database,
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
            )
        except Exception as ex:
            logger.error(
                f"Failed to connect to PostgreSQL at {self.host}:{self.port} | {ex}"
            )
            self._pool = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self._pool:
            await self.connect()
        if not self._pool:
            return None
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(data)
                results = [dict(row) for row in rows]
                return DataSourceQueryResult(len(results), results, self._name())
        except Exception as ex:
            logger.error(f"Query failed, resetting pool | {ex}")
            if self._pool:
                await self._pool.close()
            self._pool = None
            return None

    @classmethod
    def _name(cls) -> str:
        return "postgresql"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('database', str, True, 'Database name'),
            Parameters('host', str, True, 'PostgreSQL host'),
            Parameters('port', int, True, 'PostgreSQL port'),
            Parameters('username', str, True, 'Username'),
            Parameters('password', str, True, 'Password'),
        ]
