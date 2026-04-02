from typing import Any, List
from logging import getLogger
from .base import BaseDataSource, DataSourceQueryResult
from ..utils import Parameters
import aiohttp

logger = getLogger(__name__)


class LokiDataSource(BaseDataSource):
    url: str
    username: str
    password: str
    verify: bool
    org_id: str
    _session: aiohttp.ClientSession | None = None
    _base_url: str

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.org_id:
            headers["X-Scope-OrgID"] = self.org_id
        return headers

    def _auth(self) -> aiohttp.BasicAuth | None:
        if self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    async def connect(self):
        logger.debug(f"Connecting to {self.url}")
        self._base_url = self.url.rstrip("/")
        try:
            connector = aiohttp.TCPConnector(verify_ssl=self.verify)
            self._session = aiohttp.ClientSession(
                connector=connector, auth=self._auth(), headers=self._headers()
            )
            async with self._session.get(f"{self._base_url}/ready") as resp:
                resp.raise_for_status()
        except Exception as ex:
            logger.error(f"Datasource connect exception. url: {self.url} | {ex}")
            if self._session:
                await self._session.close()
            self._session = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self._session:
            await self.connect()
        if not self._session:
            return None
        try:
            logger.debug(f"Sending query to {self.url}")
            params = {"query": data, "limit": 5000}
            async with self._session.get(
                f"{self._base_url}/loki/api/v1/query_range", params=params
            ) as resp:
                resp.raise_for_status()
                payload = await resp.json()
                return await self._parse_result(payload)
        except Exception as ex:
            logger.error(f"Query failed, resetting session | {ex}")
            if self._session:
                await self._session.close()
            self._session = None
            return None

    async def _parse_result(self, payload: Any) -> DataSourceQueryResult:
        result_type = payload.get("data", {}).get("resultType", "streams")
        results = payload.get("data", {}).get("result", [])
        rows = []

        if result_type == "matrix":
            total = 0
            for series in results:
                metric = series.get("metric", {})
                values = series.get("values", [])
                for ts, value in values:
                    rows.append({"timestamp": ts, "value": value, **metric})
                if values:
                    total += float(values[-1][1])
            return DataSourceQueryResult(int(total), rows, self._name())

        for stream in results:
            labels = stream.get("stream", {})
            for ts, line in stream.get("values", []):
                rows.append({"timestamp": ts, "line": line, **labels})
        return DataSourceQueryResult(len(rows), rows, self._name())

    @classmethod
    def _name(cls) -> str:
        return "loki"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("url", str, True, "Loki url: http://localhost:3100"),
            Parameters("username", str, False, "Username", is_sensive_field=True),
            Parameters("password", str, False, "Password", is_sensive_field=True),
            Parameters("verify", bool, False, "Verify SSL", False),
            Parameters(
                "org_id", str, False, "Loki org ID (X-Scope-OrgID)", default="fake"
            ),
        ]
