from typing import Any, Dict
from logging import getLogger
import json
import aiohttp

from .base import BaseDataSource, DataSourceQueryResult

logger = getLogger(__name__)


class ElasticsearchDataSource(BaseDataSource):
    host: str
    port: int
    index: str
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    verify: bool = False
    _session: aiohttp.ClientSession | None = None

    def _base_url(self) -> str:
        scheme = "https" if self.verify else "http"
        return f"{scheme}://{self.host}:{self.port}"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"ApiKey {self.api_key}"
        return headers

    def _auth(self) -> aiohttp.BasicAuth | None:
        if self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    async def connect(self):
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            self._session = aiohttp.ClientSession(
                connector=connector, auth=self._auth(), headers=self._headers()
            )
            async with self._session.get(f"{self._base_url()}/_cluster/health") as resp:
                if resp.status != 200:
                    raise Exception(f"Elasticsearch not healthy, status: {resp.status}")
        except Exception as ex:
            logger.error(
                f"Failed to connect to Elasticsearch at {self.host}:{self.port} | {ex}"
            )
            if self._session:
                await self._session.close()
            self._session = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self._session:
            await self.connect()
        if not self._session:
            return None
        try:
            body = json.loads(data)
            async with self._session.post(
                f"{self._base_url()}/{self.index}/_search", json=body
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"HTTP {resp.status}: {text}")
                payload = await resp.json()
                return self._parse_result(payload)
        except Exception as ex:
            logger.error(f"Query failed, resetting session | {ex}")
            if self._session:
                await self._session.close()
            self._session = None
            return None

    def _parse_result(self, payload: Any) -> DataSourceQueryResult:
        hits = payload.get("hits", {}).get("hits", [])
        rows = [{"_id": h["_id"], "_index": h["_index"], **h["_source"]} for h in hits]
        return DataSourceQueryResult(len(rows), rows, self._name())

    @classmethod
    def _name(cls) -> str:
        return "elasticsearch"

    def to_dict(self) -> Dict:
        return {
            "name": self._name(),
            "host": self.host,
            "port": self.port,
            "index": self.index,
            "username": self.username,
            "password": self.password,
            "api_key": self.api_key,
            "verify": self.verify,
        }

    async def _parse(self, _obj: Any):
        host = _obj.get("host")
        port = _obj.get("port")
        index = _obj.get("index")

        if not host or not port or not index:
            raise Exception("Invalid parameters: host, port and index are required")

        self.host = host
        self.port = port
        self.index = index
        self.username = _obj.get("username")
        self.password = _obj.get("password")
        self.api_key = _obj.get("api_key")
        self.verify = _obj.get("verify", False)
