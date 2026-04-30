from typing import List, Type
from .base import BaseDataSource
from .clickhouse import ClickhouseDataSource
from .loki import LokiDataSource
from .elasticsearch import ElasticsearchDataSource
from .postgresql import PostgreSQLDataSource
from .victorialogs import VictoriaLogsDataSource
from .opensearch import OpensearchDataSource
from .databricks import DatabricksDataSource


datasources: List[Type[BaseDataSource]] = [
    ClickhouseDataSource,
    LokiDataSource,
    ElasticsearchDataSource,
    OpensearchDataSource,
    PostgreSQLDataSource,
    VictoriaLogsDataSource,
    DatabricksDataSource
]
