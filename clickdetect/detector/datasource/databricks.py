from typing import List
from logging import getLogger

from ..utils import Parameters
from .base import BaseDataSource, DataSourceQueryResult
from databricks import sql

logger = getLogger(__name__)


class DatabricksDataSource(BaseDataSource):
    host: str
    path: str
    token: str
    catalog: str | None = None

    _connection = None

    async def connect(self):
        try:
            self._connection = sql.connect(
                self.host, self.path, access_token=self.token, catalog=self.catalog
            )
        except Exception as ex:
            logger.error(
                f"Failed to connect to Databricks at {self.host} {self.path} | {str(ex)}"
            )
            self._connection = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self._connection:
            await self.connect()
        if not self._connection:
            return None

        try:
            with self._connection.cursor() as cursor:
                cexec = cursor.execute(data)
                rows = cexec.fetchall()
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )
                results = [dict(zip(columns, row)) for row in rows]
                return DataSourceQueryResult(len(results), results, self._name())

        except Exception as ex:
            logger.error(f"Query failed: {str(ex)}")
            if self._connection:
                self._connection.close()
            self._connection = None

    @classmethod
    def _name(cls) -> str:
        return "databricks"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("host", str, True, "Databricks Hostname"),
            Parameters("path", str, True, "Databricks Path http_path"),
            Parameters("token", str, True, "Databricks Token", is_sensive_field=True),
            Parameters("catalog", str, False, "Databricks Catalog"),
        ]
