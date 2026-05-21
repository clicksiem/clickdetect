from typing import Any, Dict, List
from logging import getLogger
import aiohttp

from ..utils import Parameters
from .base import BaseDataSource, DataSourceQueryResult

logger = getLogger(__name__)


class OpensearchPPLDataSource(BaseDataSource):
    url: str
    username: str | None = None
    password: str | None = None
    verify: bool = False
    _session: aiohttp.ClientSession | None = None

    def _base_url(self) -> str:
        return self.url.strip().rstrip("/")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
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
                f"Failed to connect to Opensearch at {self._base_url()} | {ex}"
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
            resp = await self._session.post(
                f"{self._base_url()}/_plugins/_sql", json={"query": data}
            )
            resp.raise_for_status()
            resp_data = await resp.json()
            logger.debug(f"Response: {resp_data}")
            return self._parse_result(resp_data)

        except Exception as ex:
            logger.error(f"Error while quering {self._name()} | {str(ex)}")
            logger.debug(f"Query data: {data}")
            return None

    def _parse_result(self, resp: Any) -> DataSourceQueryResult:
        size: int = resp.get("size", 0)
        columns = [col.get("name") for col in resp.get("schema", [])]
        result = [dict(zip(columns, rows)) for rows in resp.get("datarows", [])]
        return DataSourceQueryResult(size, result, self._name())

    @classmethod
    def _name(cls) -> str:
        return "opensearch-ppl"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("url", str, True, "Opensearch url"),
            Parameters("username", str, False, "Username", is_sensive_field=True),
            Parameters("password", str, False, "Password", is_sensive_field=True),
            Parameters("verify", bool, False, "Verify SSL", False),
        ]
