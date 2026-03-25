from typing import List, Type
from .base import BaseDataSource
from .clickhouse import ClickhouseDataSource
from .loki import LokiDataSource
from .elasticsearch import ElasticsearchDataSource
from .postgresql import PostgreSQLDataSource


datasources: List[Type[BaseDataSource]] = [
    ClickhouseDataSource,
    LokiDataSource,
    ElasticsearchDataSource,
    PostgreSQLDataSource,
]
