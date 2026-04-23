from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)


class DiscordWebhook(BaseWebhook):
    name: str
    url: str
    username: str
    avatar: str
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
            if len(data) > 2000:
                raise Exception(
                    "send error, the message is ultrapasses discord limit 2000 characters"
                )
            message_data = {
                "content": data,
            }
            if self.username:
                message_data["username"] = self.username
            if self.avatar:
                message_data["avatar_url"] = self.avatar

            logger.debug(f"sending alert to discord: {self.url}")

            async with self.session.post(
                self.url,
                json=message_data,
                ssl=self.verify,
                timeout=ClientTimeout(self.timeout),
            ) as req:
                req.raise_for_status()
                logger.info(f"alert sent to discord: {self.name}")
        except Exception as ex:
            logger.error(f"alert not sent: {self.url}")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "discord"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("url", str, True, "Discord webhook url"),
            Parameters("username", str, False, "Discord username", ""),
            Parameters("avatar", str, False, "Discord avatar url", ""),
            Parameters("verify", bool, False, "SSL verify", False),
            Parameters("timeout", int, False, "Timeout in seconds", 10),
            Parameters(
                "template",
                str,
                False,
                "Message template",
                BaseWebhook._alternative_template(),
            ),
        ]
