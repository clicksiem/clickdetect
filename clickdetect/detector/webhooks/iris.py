from typing import Any, Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters
import json

logger = getLogger(__name__)


class DfirIRISWebhook(BaseWebhook):
    name: str
    url: str
    headers: Dict[str, str]
    verify: bool
    customer_id: int
    api_key: str
    session: ClientSession

    async def close(self):
        if hasattr(self, "session") and self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.session = ClientSession()

    async def send(self, data: str, template_data: Dict):
        j_data = json.loads(data)
        rule = j_data.get("rule", {})

        level = rule.get("level", 0)
        alert_severity_id = (
            1 if level <= 3 else
            2 if level <= 7 else
            3 if level <= 10 else
            4 if level <= 13 else
            5
        )

        tags = rule.get("tags", [])
        alert_data = {
            "alert_title": rule.get("name"),
            "alert_description": rule.get("description"),
            "alert_source": j_data.get("detector", {}).get("datasource", {}).get("name"),
            "alert_severity_id": alert_severity_id,
            "alert_status_id": 2,
            "alert_source_event_time": j_data.get("time", ""),
            "alert_note": "",
            "alert_tags": ", ".join(tags) if isinstance(tags, list) else tags,
            "alert_source_content": j_data.get("data"),
            "alert_customer_id": self.customer_id,
        }

        try:
            logger.debug(f"sending alert to DFIR-IRIS at {self.url}")
            async with self.session.post(
                self.url + "/alerts/add",
                json=alert_data,
                ssl=self.verify,
                headers={**self.headers, "Authorization": f"Bearer {self.api_key}"},
                timeout=ClientTimeout(10),
            ) as resp:
                resp.raise_for_status()
                logger.info(f"Alert sent to DFIR-IRIS (status {resp.status})")
        except Exception as ex:
            logger.error("Alert not sent to DFIR-IRIS")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "iris"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('name', str, False, 'Webhook name'),
            Parameters('url', str, True, 'DFIR-IRIS base URL'),
            Parameters('api_key', str, True, 'DFIR-IRIS API key', is_sensive_field=True),
            Parameters('customer_id', int, True, 'DFIR-IRIS customer ID'),
            Parameters('headers', dict, False, 'Extra HTTP headers', {}),
            Parameters('verify', bool, False, 'SSL verify', False),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")
        self.headers = {k.lower(): v for k, v in self.headers.items()}
