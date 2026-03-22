import logging
from clickdetect.detector.webhooks.base import BaseWebhook
from typing import Any, Dict
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

    async def _parse(self, data: Any):
        url: str = data.get("url")
        owner = data.get("owner")
        repository = data.get("repository")
        token = data.get("token")

        if not url or not owner or not repository or not token:
            logger.error(f"Invalid parameters provided: {data}")
            return

        self.name = data.get("name")
        self.url = url.rstrip("/")
        self.owner = owner
        self.repository = repository
        self.token = token
        self.title = data.get("title", "alert: {{ rule.name }}")
        self.template = data.get("template", DEFAULT_TEMPLATE)

    def to_dict(self) -> Dict:
        return {
            "type": self._name(),
            "name": self.name,
            "url": self.url,
            "owner": self.owner,
            "repository": self.repository,
            "title": self.title,
            "token": self.token,
        }

    @classmethod
    def _name(cls) -> str:
        return "forgejo"
