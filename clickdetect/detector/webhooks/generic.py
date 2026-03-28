from typing import Any, Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook, BaseWebhookParameters

logger = getLogger(__name__)


class GenericWebhook(BaseWebhook):
    name: str
    url: str
    headers: Dict[str, str]
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
            logger.debug(f"sending alert to {self.url}")
            async with self.session.post(
                self.url,
                data=data,
                ssl=self.verify,
                headers=self.headers,
                timeout=ClientTimeout(self.timeout),
            ) as _:
                logger.info(f"Alert sended to {self.url}")
                pass

        except Exception as ex:
            logger.error("Alert not sended")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "generic"

    @classmethod
    def _params(cls) -> List[BaseWebhookParameters]:
        return [
            BaseWebhookParameters('name', str, False, 'Webhook name'),
            BaseWebhookParameters('url', str, True, 'Webhook URL'),
            BaseWebhookParameters('headers', dict, False, 'HTTP headers', {}),
            BaseWebhookParameters('verify', bool, False, 'SSL verify', False),
            BaseWebhookParameters('timeout', int, False, 'Timeout in seconds', 10),
            BaseWebhookParameters('template', str, False, 'Message template'),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.headers = {k.lower(): v for k, v in self.headers.items()}
        if not self.headers.get("content-type"):
            self.headers["content-type"] = "application/json"
