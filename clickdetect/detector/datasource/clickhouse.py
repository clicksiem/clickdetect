from typing import Any, Dict
from clickhouse_connect import get_async_client
from clickhouse_connect.driver.asyncclient import AsyncClient
from logging import getLogger

from .base import BaseDataSource, DataSourceQueryResult

logger = getLogger(__name__)

class ClickhouseDataSource(BaseDataSource):
    database: str
    host: str
    port: int
    username: str
    password: str
    verify: bool = False
    client: AsyncClient | None = None

    async def connect(self):
        try:
            self.client = await get_async_client(
                    database=self.database,
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    secure=self.verify
            )
        except Exception as ex:
            logger.error(f'Failed to connect to ClickHouse at {self.host}:{self.port} | {ex}')
            self.client = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self.client:
            await self.connect()
        if not self.client:
            return None
        try:
            result = await self.client.query(data)
            return DataSourceQueryResult(result.row_count, list(result.named_results()))
        except Exception as ex:
            logger.error(f'Query failed, resetting client | {ex}')
            self.client = None
            return None

    @classmethod
    def _name(cls) -> str:
        return 'clickhouse'

    def to_dict(self) -> Dict:
        return {
            'name': self._name(),
            'database': self.database,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'verify': self.verify
        }

    async def _parse(self, _obj: Any):
        database = _obj.get('database', 'default')
        host = _obj.get('host')
        port = _obj.get('port')
        username = _obj.get('username')
        password = _obj.get('password')
        verify = _obj.get('verify', False)

        if not host or not port or not username or not password:
            raise Exception(f'Invalid parameters: {self.to_dict().items()}')

        self.database = database
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.verify = verify
