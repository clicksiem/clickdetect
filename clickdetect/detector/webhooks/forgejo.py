import logging
from clickdetect.detector.webhooks.base import BaseWebhook
from clickdetect.detector.utils import Parameters
from typing import Any, Dict, List
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class ForgejoWebhook(BaseWebhook):
    name: str
    type: str
    owner: str
    token: str
    title: str
    repository: str
    session: ClientSession
    logged_in: bool = False

    async def close(self):
        if hasattr(self, "session") and self.session and not self.session.closed:
            await self.session.close()

    async def connect(self):
        self.session = ClientSession()
        async with self.session.get(
            self.url + "/api/v1/user", headers={"Authorization": f"token {self.token}"}
        ) as resp:
            resp.raise_for_status()
        logger.info("Forgejo connection ok")
        self.logged_in = True

    async def send(self, data: str, template_data: Dict):
        if not self.logged_in:
            logger.error("Forgejo not logged-in")
            raise
        title = self.jinja_env.from_string(self.title).render(**template_data)
        async with self.session.post(
            self.url + f"/api/v1/repos/{self.owner}/{self.repository}/issues",
            json={"title": title, "body": data},
            headers={"Authorization": f"token {self.token}"},
        ) as resp:
            resp.raise_for_status()
        logger.info(f"alert sent to forgejo: {self.name}")

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters("name", str, False, "Webhook name"),
            Parameters("url", str, True, "Forgejo base URL"),
            Parameters("owner", str, True, "Repository owner"),
            Parameters("repository", str, True, "Repository name"),
            Parameters("token", str, True, "API token"),
            Parameters(
                "title", str, False, "Issue title template", "alert: {{ rule.name }}"
            ),
            Parameters(
                "template",
                str,
                False,
                "Issue body template",
                BaseWebhook._alternative_template(),
            ),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")

    @classmethod
    def _name(cls) -> str:
        return "forgejo"
