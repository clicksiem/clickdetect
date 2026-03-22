from typing import Any, Dict
from jinja2 import Environment


class BaseWebhook:
    jinja_env: Environment = Environment()
    template: str = '{"rule": {{ rule }}, "data": {{ data }}, "detector": {{ detector }} }, "time": {{ time }}, "datasource": {{ datasource }} }'
    name: str
    type: str

    async def close(self):
        pass

    async def connect(self):
        pass

    async def send(
        self,
        data: str,
        template_data: Dict,
    ):  # data: rendered jinja string; template_data: raw context used to render it
        raise NotImplementedError()

    async def _parse(self, data: Any):
        raise NotImplementedError()

    def to_dict(self) -> Dict:
        raise NotADirectoryError()

    @classmethod
    def _name(cls) -> str:
        raise NotImplementedError()
