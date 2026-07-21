from typing import Any, Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters
import json

logger = getLogger(__name__)


class OpsGenieWebhook(BaseWebhook):
    severity_priorities: Dict[str, str] = {
        "informational": "P5",
        "low": "P4",
        "medium": "P3",
        "high": "P2",
        "critical": "P1",
    }

    name: str
    url: str
    headers: Dict[str, str]
    verify: bool
    api_key: str
    source: str
    severity_map: Dict[str, int]
    session: ClientSession

    async def close(self):
        if hasattr(self, "session") and self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.session = ClientSession()

    async def send(self, data: str, template_data: Dict):
        j_data = json.loads(data)
        rule = j_data.get("rule", {})
        detector = j_data.get("detector", {})

        level = rule.get("level", 0)
        priority = self.severity_priorities[self._severity(level)]

        tags = rule.get("tags", [])
        alert_data = {
            "message": rule.get("name"),
            "description": rule.get("description") or rule.get("name"),
            "priority": priority,
            "source": self.source,
            "alias": str(rule.get("id")),
            "tags": tags if isinstance(tags, list) else [tags],
            "details": {
                "rule_id": str(rule.get("id")),
                "detector": str(detector.get("name")),
                "tenant": str(detector.get("tenant")),
            },
        }

        try:
            logger.debug(f"sending alert to OpsGenie at {self.url}")
            async with self.session.post(
                self.url,
                json=alert_data,
                ssl=self.verify,
                headers={
                    **self.headers,
                    "Authorization": f"GenieKey {self.api_key}",
                },
                timeout=ClientTimeout(10),
            ) as resp:
                resp.raise_for_status()
                logger.info(f"alert sent to OpsGenie (status {resp.status})")
        except Exception as ex:
            logger.error("alert not sent to OpsGenie")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "opsgenie"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters(
                "url",
                str,
                False,
                "OpsGenie alerts API URL",
                "https://api.opsgenie.com/v2/alerts",
            ),
            Parameters(
                "api_key", str, True, "OpsGenie API key", is_sensive_field=True
            ),
            Parameters("source", str, False, "Alert source", "clickdetect"),
            cls._severity_param(),
            Parameters("headers", dict, False, "Extra HTTP headers", {}),
            Parameters("verify", bool, False, "SSL verify", False),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")
        self.headers = {k.lower(): v for k, v in self.headers.items()}
