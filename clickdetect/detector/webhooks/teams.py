from typing import Dict, List
from aiohttp import ClientSession, ClientTimeout
from logging import getLogger
from .base import BaseWebhook
from ..utils import Parameters

logger = getLogger(__name__)

DEFAULT_TEMPLATE = """{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "{{ rule.name }}",
    "sections": [{
        "activityTitle": "**[Level {{ rule.level }}] {{ rule.name }}**",
        "activitySubtitle": "{{ rule.description }}",
        "facts": [
            { "name": "Rule ID", "value": "{{ rule.id }}" },
            { "name": "Group", "value": "{{ rule.group }}" },
            { "name": "Tags", "value": "{{ rule.tags | join(', ') }}" },
            { "name": "Matches", "value": "{{ data.len }}" },
            { "name": "Detector", "value": "{{ detector.name }}" },
            { "name": "Tenant", "value": "{{ detector.tenant }}" }
        ],
        "markdown": true
    }{% if clickagentic is defined %},{
        "activityTitle": "**Clickagentic Analysis**",
        "facts": [
            { "name": "Title", "value": {{ clickagentic.title | tojson }} },
            { "name": "Summary", "value": {{ clickagentic.summary | tojson }} },
            { "name": "Severity", "value": {{ (clickagentic.severity ~ " (confidence: " ~ clickagentic.confidence ~ "%)") | tojson }} },
            { "name": "Risk Score", "value": "{{ clickagentic.risk_score }}%" },
            { "name": "False Positive Score", "value": "{{ clickagentic.false_positive_score }}%" },
            { "name": "Explanation", "value": {{ clickagentic.explanation | tojson }} },
            { "name": "Mitigations", "value": {{ clickagentic.mitigations | join('\n') | tojson }} }{% if clickagentic.affected_entities %},
            { "name": "Affected Entities", "value": {{ clickagentic.affected_entities | join(', ') | tojson }} }{% endif %}{% if clickagentic.recommended_action %},
            { "name": "Recommended Action", "value": {{ clickagentic.recommended_action | tojson }} }{% endif %}
        ],
        "markdown": true
    }{% endif %}]
}"""


class TeamsWebhook(BaseWebhook):
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

    async def send(self, data: str, template_data: Dict):
        try:
            logger.debug(f"sending alert to Teams: {self.url}")
            async with self.session.post(
                self.url,
                data=data,
                ssl=self.verify,
                headers={"content-type": "application/json"},
                timeout=ClientTimeout(self.timeout),
            ) as req:
                req.raise_for_status()
                logger.info(f"alert sent to Teams: {self.name}")
        except Exception as ex:
            logger.error("alert not sent to Teams")
            logger.error(data)
            logger.error(str(ex))

    @classmethod
    def _name(cls) -> str:
        return "teams"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('name', str, False, 'Webhook name'),
            Parameters('url', str, True, 'Teams webhook URL'),
            Parameters('verify', bool, False, 'SSL verify', False),
            Parameters('timeout', int, False, 'Timeout in seconds', 10),
            Parameters('template', str, False, 'Message template', DEFAULT_TEMPLATE),
        ]
