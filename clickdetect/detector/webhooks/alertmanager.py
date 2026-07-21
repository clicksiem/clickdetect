from typing import Any, Dict, List
from aiohttp import ClientSession, ClientTimeout
from datetime import datetime, timedelta, timezone
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters
import json

logger = getLogger(__name__)


class AlertManagerWebhook(BaseWebhook):
    severity_labels: Dict[str, str] = {
        "informational": "info",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "critical": "critical",
    }

    name: str
    url: str
    headers: Dict[str, str]
    verify: bool
    labels: Dict[str, str]
    severity_map: Dict[str, int]
    generator_url: str
    expire_after: int
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
        time = j_data.get("time", {})

        level = rule.get("level", 0)
        severity = self.severity_labels[self._severity(level)]

        labels = {
            "alertname": rule.get("name"),
            "severity": severity,
            "level": level,
            "rule_id": rule.get("id"),
            "group": rule.get("group"),
            "detector": detector.get("name"),
            "tenant": detector.get("tenant"),
            "source": "clickdetect",
            **self.labels,
        }
        # alertmanager only accepts string label values and rejects empty ones
        labels = {k: str(v) for k, v in labels.items() if v not in (None, "")}

        tags = rule.get("tags", [])
        result_data = j_data.get("data")
        annotations = {
            "summary": rule.get("name") or "",
            "description": rule.get("description") or rule.get("name") or "",
            "tags": ",".join(tags if isinstance(tags, list) else [tags]),
            "results": json.dumps(result_data) if result_data is not None else "",
        }

        starts_at = datetime.fromtimestamp(
            time.get("startime") or datetime.now(timezone.utc).timestamp(),
            timezone.utc,
        )
        alert_data: Dict[str, Any] = {
            "labels": labels,
            "annotations": annotations,
            "startsAt": starts_at.isoformat(),
        }

        if self.expire_after > 0:
            alert_data["endsAt"] = (
                starts_at + timedelta(seconds=self.expire_after)
            ).isoformat()

        if self.generator_url:
            alert_data["generatorURL"] = self.generator_url

        try:
            logger.debug(f"sending alert to AlertManager at {self.url}")
            async with self.session.post(
                self.url + "/api/v2/alerts",
                json=[alert_data],
                ssl=self.verify,
                headers=self.headers,
                timeout=ClientTimeout(10),
            ) as resp:
                resp.raise_for_status()
                logger.info(f"alert sent to AlertManager (status {resp.status})")
        except Exception as ex:
            logger.error("alert not sent to AlertManager")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "alertmanager"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("url", str, True, "AlertManager base URL"),
            Parameters("labels", dict, False, "Extra alert labels", {}),
            cls._severity_param(),
            Parameters("generator_url", str, False, "URL of the alert source", ""),
            Parameters(
                "expire_after",
                int,
                False,
                "Seconds until the alert auto resolves (0 to disable)",
                0,
            ),
            Parameters("headers", dict, False, "Extra HTTP headers", {}),
            Parameters("verify", bool, False, "SSL verify", False),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")
        self.headers = {k.lower(): v for k, v in self.headers.items()}
        self.labels = {k: str(v) for k, v in self.labels.items()}
