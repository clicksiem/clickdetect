from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)

DEFAULT_TEMPLATE = """\
*[ALERT] {{ rule.name }}*
{% if rule.description %}
{{ rule.description }}
{% endif %}
*Rule ID*  : {{ rule.id }}
*Level*    : {{ rule.level }}
*Group*    : {{ rule.group or "-" }}
*Tags*     : {{ rule.tags | to_list or "-" }}
*Author*   : {{ rule.author | to_list or "-" }}
*Detector* : {{ detector.name }} (tenant: {{ detector.tenant }})
*Interval* : {{ detector.for_time }}
*Matches*  : {{ data.len }}\
"""


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
            resp = await self.session.post(f'{self._base_url()}', json={"text": data}, ssl=self.verify, timeout=ClientTimeout(self.timeout))
            if resp.status != 200:
                body = await resp.text()
                logger.error(f"Slack webhook returned {resp.status}: {body}")
            resp.raise_for_status()
            logger.info(f"Alert sent to Slack: {self.url}")
        except Exception as ex:
            logger.error("Alert not sent to Slack")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "slack"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('name', str, False, 'Webhook name'),
            Parameters('url', str, True, 'Slack Incoming Webhook URL'),
            Parameters('verify', bool, False, 'SSL verify', True),
            Parameters('timeout', int, False, 'Timeout in seconds', 10),
            Parameters('template', str, False, 'Message template', DEFAULT_TEMPLATE),
        ]
