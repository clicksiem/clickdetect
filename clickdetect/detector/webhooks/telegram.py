from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)

DEFAULT_TEMPLATE = """
[ALERT] {{ rule.name }}
{% if rule.description %}
{{ rule.description }}
{% endif %}
Rule ID  : {{ rule.id }}
Level    : {{ rule.level }}
Group    : {{ rule.group or "-" }}
Tags     : {{ rule.tags | to_list or "-" }}
Author   : {{ rule.author | to_list or "-" }}
Detector : {{ detector.name }} (tenant: {{ detector.tenant }})
Interval : {{ detector.for_time }}
Matches  : {{ data.len }}
"""


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
                data={"chat_id": self.chat_id, "text": data},
                ssl=self.verify,
                headers={"content-type": "application/json"},
                timeout=ClientTimeout(self.timeout),
            ) as req:
                if req.status != 200:
                    body = await req.text()
                    logger.error(f"telegram webhook returned {req.status}: {body}")
                else:
                    logger.info(f"alert sent to telegram: {self.chat_id}")
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
            Parameters("template", str, False, "Message template", DEFAULT_TEMPLATE),
        ]
