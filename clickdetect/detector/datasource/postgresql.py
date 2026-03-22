from typing import Any, Dict
from logging import getLogger
import asyncpg
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
            logger.error(f'Failed to connect to PostgreSQL at {self.host}:{self.port} | {ex}')
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
                return DataSourceQueryResult(len(results), results)
        except Exception as ex:
            logger.error(f'Query failed, resetting pool | {ex}')
            if self._pool:
                await self._pool.close()
            self._pool = None
            return None

    @classmethod
    def _name(cls) -> str:
        return 'postgresql'

    def to_dict(self) -> Dict:
        return {
            'name': self._name(),
            'database': self.database,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
        }

    async def _parse(self, _obj: Any):
        database = _obj.get('database')
        host = _obj.get('host')
        port = _obj.get('port')
        username = _obj.get('username')
        password = _obj.get('password')

        if not database or not host or not port or not username or not password:
            raise Exception('Invalid parameters: database, host, port, username and password are required')

        self.database = database
        self.host = host
        self.port = port
        self.username = username
        self.password = password
