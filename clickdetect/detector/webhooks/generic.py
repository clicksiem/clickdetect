from typing import Any, Dict
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook

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

    def to_dict(self) -> Dict:
        return {
            "type": GenericWebhook._name(),
            "name": self.name,
            "url": self.url,
            "headers": self.headers,
            "verify": self.verify,
            "timeout": self.timeout,
            "template": self.template,
        }

    async def _parse(self, data: Any):
        name = data.get("name")
        url = data.get("url")
        headers = data.get("headers", {})
        verify = data.get("verify", False)
        timeout = data.get("timeout", 10)
        template = data.get("template", self.template)

        headers = {k.lower(): v for k, v in headers.items()}
        if not headers.get("content-type"):
            headers["content-type"] = "application/json"

        self.name = name
        self.url = url
        self.headers = headers
        self.verify = verify
        self.timeout = timeout
        self.template = template
