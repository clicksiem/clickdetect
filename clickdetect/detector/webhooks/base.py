from typing import Any, Dict, List
from jinja2 import Environment
from ..utils import Parameters

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
Results  : {{ data.value }}
"""


class BaseWebhook:
    jinja_env: Environment = Environment()
    template: str = '{ "rule": {{ rule }}, "data": {{ data }}, "detector": {{ detector }}, "time": {{ time }} }'
    name: str
    type: str
    params: List[Parameters] = []

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
        self.params = self._params()

        if missing := next(
            (p.name for p in self.params if p.required and p.name not in data), None
        ):
            raise ValueError(f"Required param not provided: {missing}")

        for param in self.params:
            value = data.get(param.name, param.default)
            if value is None:
                continue
            if param.type is not None:
                if param.type is list:
                    value = [value] if not isinstance(value, list) else value
                else:
                    value = param.type(value)
            setattr(self, param.attr_name or param.name, value)

    def to_dict(self) -> Dict:
        result: Dict[str, Any] = {"type": self._name()}
        for param in self._params():
            attr = param.attr_name or param.name
            result[param.name] = getattr(self, attr, param.default)
        return result

    @classmethod
    def _name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def _params(cls) -> List[Parameters]:
        raise NotImplementedError()

    @classmethod
    def _alternative_template(cls) -> str:
        return DEFAULT_TEMPLATE
