from ..utils import Parameters
from typing import List
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
                secure=self.verify,
            )
        except Exception as ex:
            logger.error(
                f"Failed to connect to ClickHouse at {self.host}:{self.port} | {ex}"
            )
            self.client = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self.client:
            await self.connect()
        if not self.client:
            return None
        try:
            result = await self.client.query(data)
            return DataSourceQueryResult(result.row_count, list(result.named_results()), self._name())
        except Exception as ex:
            logger.error(f"Query failed, resetting client | {ex}")
            self.client = None
            return None

    @classmethod
    def _name(cls) -> str:
        return "clickhouse"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('database', str, False, 'Clickhouse database', 'default'),
            Parameters('host', str, True, 'Clickhouse host', is_sensive_field=True),
            Parameters('port', int, False, 'Clickhouse port', 8123),
            Parameters('username', str, False, 'Clickhouse username', 'default', is_sensive_field=True),
            Parameters('password', str, False, 'Clickhouse password', 'default', is_sensive_field=True),
            Parameters('verify', bool, False, 'Verify SSL connection', False),
        ]
