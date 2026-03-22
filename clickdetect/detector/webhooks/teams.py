from typing import Any, Dict
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook

logger = getLogger(__name__)

DEFAULT_TEMPLATE = """{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "{{ rule.name }}",
    "sections": [{
        "activityTitle": "**[Level {{ rule.level }}] {{ rule.name }}**",
        "activitySubtitle": "{{ rule.description }}",
        "facts": [
            { "name": "Rule ID", "value": "{{ rule.id }}" },
            { "name": "Group", "value": "{{ rule.group }}" },
            { "name": "Tags", "value": "{{ rule.tags | join(', ') }}" },
            { "name": "Matches", "value": "{{ data.len }}" },
            { "name": "Detector", "value": "{{ detector.name }}" },
            { "name": "Tenant", "value": "{{ detector.tenant }}" }
        ],
        "markdown": true
    }]
}"""


class TeamsWebhook(BaseWebhook):
    name: str
    url: str
    verify: bool
    timeout: int
    template: str
    session: ClientSession

    async def close(self):
        if hasattr(self, "session") and self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.session = ClientSession()

    async def send(self, data: str, template_data: Dict):
        try:
            logger.debug(f"sending alert to Teams: {self.url}")
            async with self.session.post(
                self.url,
                data=data,
                ssl=self.verify,
                headers={"content-type": "application/json"},
                timeout=ClientTimeout(self.timeout),
            ) as req:
                if req.status != 200:
                    body = await req.text()
                    logger.error(f"Teams webhook returned {req.status}: {body}")
                else:
                    logger.info(f"Alert sent to Teams: {self.url}")
        except Exception as ex:
            logger.error(f"Alert not sent to Teams")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "teams"

    def to_dict(self) -> Dict:
        return {
            "type": TeamsWebhook._name(),
            "name": self.name,
            "url": self.url,
            "verify": self.verify,
            "timeout": self.timeout,
            "template": self.template,
        }

    async def _parse(self, data: Any):
        url = data.get("url")
        if not url:
            raise Exception("Invalid parameters: url is required")

        self.name = data.get("name")
        self.url = url
        self.verify = data.get("verify", False)
        self.timeout = data.get("timeout", 10)
        self.template = data.get("template", DEFAULT_TEMPLATE)
