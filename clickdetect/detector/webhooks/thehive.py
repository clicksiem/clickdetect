from typing import Any, Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters
import json
import uuid

logger = getLogger(__name__)


class TheHiveWebhook(BaseWebhook):
    name: str
    url: str
    headers: Dict[str, str]
    verify: bool
    api_key: str
    alert_type: str
    source: str
    tlp: int
    pap: int
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
        severity = 1 if level <= 3 else 2 if level <= 7 else 3 if level <= 10 else 4

        tags = rule.get("tags", [])
        result_data = j_data.get("data")
        alert_data = {
            "type": self.alert_type,
            "source": self.source,
            "sourceRef": str(uuid.uuid4()),
            "title": rule.get("name"),
            "description": rule.get("description") or rule.get("name"),
            "severity": severity,
            "tlp": self.tlp,
            "pap": self.pap,
            "tags": tags if isinstance(tags, list) else [tags],
            "summary": json.dumps(result_data) if result_data is not None else "",
        }

        try:
            logger.debug(f"sending alert to TheHive at {self.url}")
            async with self.session.post(
                self.url + "/api/v1/alert",
                json=alert_data,
                ssl=self.verify,
                headers={**self.headers, "Authorization": f"Bearer {self.api_key}"},
                timeout=ClientTimeout(10),
            ) as resp:
                resp.raise_for_status()
                logger.info(f"alert sent to TheHive (status {resp.status})")
        except Exception as ex:
            logger.error("alert not sent to TheHive")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "thehive"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("url", str, True, "TheHive base URL"),
            Parameters(
                "api_key", str, True, "TheHive API key", is_sensive_field=True
            ),
            Parameters(
                "type",
                str,
                False,
                "Alert type",
                "clickdetect",
                attr_name="alert_type",
            ),
            Parameters("source", str, False, "Alert source", "clickdetect"),
            Parameters("tlp", int, False, "Traffic Light Protocol level (0-4)", 2),
            Parameters(
                "pap", int, False, "Permissible Actions Protocol level (0-4)", 2
            ),
            Parameters("headers", dict, False, "Extra HTTP headers", {}),
            Parameters("verify", bool, False, "SSL verify", False),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")
        self.headers = {k.lower(): v for k, v in self.headers.items()}
