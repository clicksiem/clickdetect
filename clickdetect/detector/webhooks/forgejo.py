import logging
from clickdetect.detector.webhooks.base import BaseWebhook, BaseWebhookParameters
from typing import Any, Dict, List
from requests import Session

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = """\
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


class ForgejoWebhook(BaseWebhook):
    name: str
    type: str
    session = Session()
    logged_in: bool = False

    async def connect(self):
        res = self.session.get(
            self.url + "/api/v1/user", headers={"Authorization": f"token {self.token}"}
        )
        res.raise_for_status()
        logger.info("Forgejo connection ok")
        self.logged_in = True

    async def send(self, data: str, template_data: Dict):
        if not self.logged_in:
            logger.error("Forgejo not logged-in")
            raise
        title = self.jinja_env.from_string(self.title).render(**template_data)
        res = self.session.post(
            self.url + f"/api/v1/repos/{self.owner}/{self.repository}/issues",
            json={"title": title, "body": data},
            headers={"Authorization": f"token {self.token}"},
        )
        res.raise_for_status()

    @classmethod
    def _params(cls) -> List[BaseWebhookParameters]:
        return [
            BaseWebhookParameters('name', str, False, 'Webhook name'),
            BaseWebhookParameters('url', str, True, 'Forgejo base URL'),
            BaseWebhookParameters('owner', str, True, 'Repository owner'),
            BaseWebhookParameters('repository', str, True, 'Repository name'),
            BaseWebhookParameters('token', str, True, 'API token'),
            BaseWebhookParameters('title', str, False, 'Issue title template', 'alert: {{ rule.name }}'),
            BaseWebhookParameters('template', str, False, 'Issue body template', DEFAULT_TEMPLATE),
        ]

    async def _parse(self, data: Any):
        await super()._parse(data)
        self.url = self.url.rstrip("/")

    @classmethod
    def _name(cls) -> str:
        return "forgejo"
