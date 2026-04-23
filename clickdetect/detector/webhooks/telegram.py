from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)

class TelegramWebhook(BaseWebhook):
    name: str
    token: str
    chat_id: str
    verify: bool
    template: str
    timeout: int
    session: ClientSession

    async def close(self):
        if hasattr(self, "session") and self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.session = ClientSession()

    async def send(self, data: str, template_data: Dict):
        try:
            logger.debug(f"sending alert to telegram: {self.chat_id}")
            async with self.session.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": self.chat_id, "text": data},
                ssl=self.verify,
                timeout=ClientTimeout(self.timeout),
            ) as req:
                req.raise_for_status()
                logger.info(f'alert sent to telegram: {self.name}')
        except Exception as ex:
            logger.error(f"alert not sent: {self.chat_id}")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "telegram"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("token", str, True, "Telegram bot token"),
            Parameters("chat_id", str, True, "Telegram chat id"),
            Parameters("verify", bool, False, "SSL verify", False),
            Parameters("timeout", int, False, "Timeout in seconds", 10),
            Parameters("template", str, False, "Message template", BaseWebhook._alternative_template()),
        ]
