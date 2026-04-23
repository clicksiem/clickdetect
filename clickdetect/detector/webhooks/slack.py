from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)


class SlackWebhook(BaseWebhook):
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

    def _base_url(self):
        return self.url.strip()

    async def send(self, data: str, template_data: Dict):
        try:
            logger.debug(f"sending alert to Slack: {self._base_url()}")
            async with self.session.post(
                f"{self._base_url()}",
                json={"text": data},
                ssl=self.verify,
                timeout=ClientTimeout(self.timeout),
            ) as resp:
                resp.raise_for_status()
            logger.info(f"alert sent to Slack: {self.name}")
        except Exception as ex:
            logger.error("alert not sent to Slack")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "slack"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("url", str, True, "Slack Incoming Webhook URL"),
            Parameters("verify", bool, False, "SSL verify", True),
            Parameters("timeout", int, False, "Timeout in seconds", 10),
            Parameters(
                "template",
                str,
                False,
                "Message template",
                BaseWebhook._alternative_template(),
            ),
        ]
