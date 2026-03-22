from typing import Any, Dict
from logging import getLogger
from .base import BaseDataSource, DataSourceQueryResult
import aiohttp

logger = getLogger(__name__)

class LokiDataSource(BaseDataSource):
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    verify: bool = False
    org_id: str | None = None
    _session: aiohttp.ClientSession | None = None

    def _base_url(self) -> str:
        scheme = 'https' if self.verify else 'http'
        return f'{scheme}://{self.host}:{self.port}'

    def _headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.org_id:
            headers['X-Scope-OrgID'] = self.org_id
        return headers

    def _auth(self) -> aiohttp.BasicAuth | None:
        if self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    async def connect(self):
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            self._session = aiohttp.ClientSession(
                connector=connector,
                auth=self._auth(),
                headers=self._headers()
            )
            async with self._session.get(f'{self._base_url()}/ready') as resp:
                if resp.status != 200:
                    raise Exception(f'Loki not ready, status: {resp.status}')
        except Exception as ex:
            logger.error(f'Failed to connect to Loki at {self.host}:{self.port} | {ex}')
            if self._session:
                await self._session.close()
            self._session = None

    async def query(self, data: str) -> DataSourceQueryResult | None:
        if not self._session:
            await self.connect()
        if not self._session:
            return None
        try:
            params = {'query': data, 'limit': 5000}
            async with self._session.get(
                f'{self._base_url()}/loki/api/v1/query_range',
                params=params
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f'HTTP {resp.status}: {body}')
                payload = await resp.json()
                return await self._parse_result(payload)
        except Exception as ex:
            logger.error(f'Query failed, resetting session | {ex}')
            if self._session:
                await self._session.close()
            self._session = None
            return None

    async def _parse_result(self, payload: Any) -> DataSourceQueryResult:
        result_type = payload.get('data', {}).get('resultType', 'streams')
        results = payload.get('data', {}).get('result', [])

        if result_type == 'matrix':
            rows = []
            total = 0
            for series in results:
                metric = series.get('metric', {})
                values = series.get('values', [])
                for ts, value in values:
                    rows.append({'timestamp': ts, 'value': value, **metric})
                if values:
                    total += float(values[-1][1])
            return DataSourceQueryResult(int(total), rows)

        rows = []
        for stream in results:
            labels = stream.get('stream', {})
            for ts, line in stream.get('values', []):
                rows.append({'timestamp': ts, 'line': line, **labels})
        return DataSourceQueryResult(len(rows), rows)

    @classmethod
    def _name(cls) -> str:
        return 'loki'

    def to_dict(self) -> Dict:
        return {
            'name': self._name(),
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'verify': self.verify,
            'org_id': self.org_id,
        }

    async def _parse(self, _obj: Any):
        host = _obj.get('host')
        port = _obj.get('port', 3100)
        username = _obj.get('username')
        password = _obj.get('password')
        verify = _obj.get('verify', False)
        org_id = _obj.get('org_id')

        if not host:
            raise Exception(f'Invalid parameters: host are required')

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.verify = verify
        self.org_id = org_id
