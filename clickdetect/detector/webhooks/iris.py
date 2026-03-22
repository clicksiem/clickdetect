from typing import Any, Dict
from logging import getLogger
from .base import BaseWebhook
import json

logger = getLogger(__name__)


class DfirIRISWebhook(BaseWebhook):
    def __init__(self) -> None:
        raise NotImplementedError()

    async def close(self):
        pass

    async def connect(self):
        pass

    async def send(self, data: str, template_data: Dict):
        j_data = json.loads(data)
        alert_data = {
            "alert_title": j_data.get("rule").get("name"),
            "alert_description": j_data.get("rule").get("description"),
            "alert_source": j_data.get("detector").get("datasource").get("name"),
            "alert_severity_id": 1,
            "alert_status_id": 2,
            "alert_source_event_time": "",
            "alert_note": "",
            "alert_tags": "",
            "alert_customer_id": self.customer_id,
        }

    @classmethod
    def _name(cls) -> str:
        return "iris"

    def to_dict(self) -> Dict:
        return {
            "type": DfirIRISWebhook._name(),
            "name": self.name,
            "url": self.url,
            "headers": self.headers,
            "verify": self.verify,
            "template": self.template,
        }

    async def _parse(self, data: Any):
        name = data.get("name")
        verify = data.get("verify", False)
        url = data.get("url")
        headers = data.get("headers")
        customer_id = data.get("customer_id")

        self.name = name
        self.url = url
        self.verify = verify
        self.headers = headers
        self.customer_id = customer_id
