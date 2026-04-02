from typing import List
from logging import getLogger
from .base import BaseDataSource, DataSourceQueryResult
from ..utils import Parameters

import aiohttp
import json

logger = getLogger(__name__)


class VictoriaLogsDataSource(BaseDataSource):
    url: str
    username: str
    password: str
    verify: bool
    account_id: str
    project_id: str
    _session: aiohttp.ClientSession | None = None
    _base_url: str

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.account_id:
            headers["X-VictoriaMetrics-Account-Id"] = self.account_id
        if self.project_id:
            headers["X-VictoriaMetrics-Project-Id"] = self.project_id
        return headers

    def _auth(self) -> aiohttp.BasicAuth | None:
        if self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    async def connect(self):
        logger.debug(f"Connecting to {self.url}")
        self._base_url = self.url.rstrip("/")
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            self._session = aiohttp.ClientSession(
                connector=connector, auth=self._auth(), headers=self._headers()
            )
            async with self._session.get(f"{self._base_url}/health") as resp:
                if resp.status != 200:
                    raise Exception(f"VictoriaLogs not ready, status: {resp.status}")
        except Exception as ex:
            logger.error(f"Failed to connect to VictoriaLogs at {self.url} | {ex}")
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
                f"{self._base_url}/select/logsql/query", params=params
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"HTTP {resp.status}: {body}")
                body = await resp.text()
                return self._parse_result(body)
        except Exception as ex:
            logger.error(f"Query failed, resetting session | {ex}")
            if self._session:
                await self._session.close()
            self._session = None
            return None

    def _parse_result(self, body: str) -> DataSourceQueryResult:
        rows = []
        for line in body.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return DataSourceQueryResult(len(rows), rows, self._name())

    @classmethod
    def _name(cls) -> str:
        return "victorialogs"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("url", str, True, "VictoriaLogs url"),
            Parameters("username", str, False, "Username", is_sensive_field=True),
            Parameters("password", str, False, "Password", is_sensive_field=True),
            Parameters("verify", bool, False, "Verify SSL", False),
            Parameters(
                "account_id", str, False, "X-VictoriaMetrics-Account-Id header", "0"
            ),
            Parameters(
                "project_id", str, False, "X-VictoriaMetrics-Project-Id header", "0"
            ),
        ]
