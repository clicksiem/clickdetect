from typing import Any, Dict, List
from logging import getLogger
import json
import aiohttp

from ..utils import Parameters
from .base import BaseDataSource, DataSourceQueryResult

logger = getLogger(__name__)


class ElasticsearchDataSource(BaseDataSource):
    url: str
    index: str
    username: str | None = None
    password: str | None = None
    api_key: str | None = None
    verify: bool = False
    _session: aiohttp.ClientSession | None = None

    def _base_url(self) -> str:
        return self.url.strip().rstrip("/")

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
            logger.info(f"Conneting to {self._base_url()}")
            connector = aiohttp.TCPConnector(ssl=False)
            self._session = aiohttp.ClientSession(
                connector=connector, auth=self._auth(), headers=self._headers()
            )
            resp = await self._session.get(f"{self._base_url()}/_cluster/health")
            if resp.status != 200:
                logger.error("Datasource not healthy")
            resp.raise_for_status()
        except Exception as ex:
            logger.error(
                f"Failed to connect to Elasticsearch at {self._base_url()} | {ex}"
            )
            if self._session:
                await self._session.close()
            self._session = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        logger.debug("Quering datasource")
        if not self._session:
            await self.connect()
        if not self._session:
            logger.error("Session not ok")
            return None
        try:
            body = json.loads(data)
            resp = await self._session.post(
                f"{self._base_url()}/{self.index}/_search", json=body
            )
            resp.raise_for_status()
            jdata = await resp.json()
            return self._parse_result(jdata)
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

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("url", str, True, "Elasticsearch url"),
            Parameters("index", str, True, "Elasticsearch index"),
            Parameters("username", str, False, "Username", is_sensive_field=True),
            Parameters("password", str, False, "Password", is_sensive_field=True),
            Parameters("api_key", str, False, "API key"),
            Parameters("verify", bool, False, "Verify SSL", False),
        ]
