from typing import List
from logging import getLogger
from ..utils import Parameters
from .base import BaseDataSource, DataSourceQueryResult
import duckdb

logger = getLogger(__name__)


class DuckDBDataSource(BaseDataSource):
    database: str
    s3_key: str
    s3_secret: str
    s3_host: str
    s3_region: str
    s3_type: str  # Literal['s3', 'gcs', 'r2']
    r2_account: str
    ssl: bool
    verify: bool
    supported_s3_type = {"s3", "gcs", "r2"}

    connection: duckdb.DuckDBPyConnection | None = None

    async def connect(self):
        try:
            self.connection = duckdb.connect(
                self.database, read_only=self.database != ":memory:"
            )

            if self.s3_key:
                if self.s3_type not in self.supported_s3_type:
                    raise ValueError(f"Unsupported s3 type {self.s3_type}")

                secret_sql_parts = [
                    f"TYPE {self.s3_type}",
                    "PROVIDER config",
                    f"KEY_ID '{self.s3_key}'",
                    f"SECRET '{self.s3_secret}'",
                    f"REGION '{self.s3_region}'",
                    f"ENDPOINT '{self.s3_host}'",
                    f"USE_SSL {str(self.ssl).lower()}",
                    f"VERIFY_SSL {str(self.verify).lower()}",
                ]

                if self.s3_type == "r2" and self.r2_account:
                    secret_sql_parts.append(f"ACCOUNT_ID '{self.r2_account}'")

                secret_sql = (
                    f"CREATE OR REPLACE SECRET secret ( {', '.join(secret_sql_parts)} )"
                )

                logger.debug(f"Secret sql: {secret_sql}")

                self.connection.execute(secret_sql)

        except Exception as ex:
            logger.error(f"Failed to connect to DuckDB at {self.database} | {ex}")

            if self.connection:
                self.connection.close()
            self.connection = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self.connection:
            await self.connect()
        if not self.connection:
            return None
        try:
            rel = self.connection.sql(data)
            columns = rel.columns
            results = [dict(zip(columns, row)) for row in rel.fetchall()]
            return DataSourceQueryResult(len(results), results, self._name())
        except Exception as ex:
            logger.error(f"Query failed | {ex}")
            return None

    @classmethod
    def _name(cls) -> str:
        return "duckdb"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters(
                "database", str, True, "Database name or :memory:", default=":memory:"
            ),
            Parameters("s3_key", str, False, "S3 key", default=""),
            Parameters("s3_secret", str, False, "S3 secret", default=""),
            Parameters("s3_host", str, False, "S3 host", default="s3.amazonaws.com"),
            Parameters("s3_region", str, False, "S3 region", default="us-east-1"),
            Parameters("s3_type", str, False, "S3 type (s3, r2, gcs)", default="s3"),
            Parameters("r2_account", str, False, "R2 account", default=""),
            Parameters("ssl", bool, False, "Use SSL", default=True),
            Parameters("verify", bool, False, "SSL Verify", default=True),
        ]
