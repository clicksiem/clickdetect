from typing import Any, Dict, List
from jinja2 import Environment
from ..utils import Parameters

DEFAULT_TEMPLATE = """
[ALERT] {{ rule.name }}
{% if rule.description %}
{{ rule.description }}
{% endif %}
Rule ID: {{ rule.id }}
Level: {{ rule.level }}
Group: {{ rule.group or "-" }}
Tags: {{ rule.tags | to_list or "-" }}
Author: {{ rule.author | to_list or "-" }}
Detector: {{ detector.name }} (tenant: {{ detector.tenant }})
Interval: {{ detector.for_time }}
Matches: {{ data.len }}
Results: {{ data.value }}
{% if clickagentic is defined %}
--- clickagentic
## plugin - Clickagentic
Title: {{ clickagentic.title }}
Summary: {{ clickagentic.summary }}
Severity: {{ clickagentic.severity }} (confidence: {{ clickagentic.confidence }}%)
Risk Score: {{ clickagentic.risk_score }}%
False Positive Score: {{ clickagentic.false_positive_score }}%
Explanation: {{ clickagentic.explanation }}
{% if clickagentic.affected_entities %}Affected Entities:
{% for e in clickagentic.affected_entities %}- {{ e }}
{% endfor %}{% endif %}Mitigations:
{% for m in clickagentic.mitigations %}- {{ m }}
{% endfor %}{% if clickagentic.recommended_action %}Recommended Action: {{ clickagentic.recommended_action }}
{% endif %}{% endif %}"""


class BaseWebhook:
    jinja_env: Environment = Environment()
    template: str = '{ "rule": {{ rule }}, "data": {{ data }}, "detector": {{ detector }}, "time": {{ time }} }'
    name: str
    type: str
    params: List[Parameters] = []

    # severity band -> minimum rule level, each webhook translates the band
    # into the severity vocabulary of its destination
    DEFAULT_SEVERITY_MAP: Dict[str, int] = {
        "informational": 0,
        "low": 20,
        "medium": 40,
        "high": 60,
        "critical": 80,
    }
    severity_map: Dict[str, int] = DEFAULT_SEVERITY_MAP

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

    def _severity(self, level: Any) -> str:
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 0

        bands = sorted(self.severity_map.items(), key=lambda band: band[1])
        severity = bands[0][0]
        for name, minimum in bands:
            if level >= minimum:
                severity = name
        return severity

    def _parse_severity_map(self, data: Dict[str, Any]) -> Dict[str, int]:
        severity_map = dict(self.DEFAULT_SEVERITY_MAP)
        for name, level in data.items():
            if name not in severity_map:
                raise ValueError(
                    f"Unknown severity: {name}, expected one of: "
                    f"{', '.join(severity_map)}"
                )
            try:
                level = int(level)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid severity level: {name}: {level}")

            if not 0 <= level <= 100:
                raise ValueError(
                    f"Severity level must be between 0 and 100: {name}: {level}"
                )
            severity_map[name] = level
        return severity_map

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

        if any(param.name == "severity_map" for param in self.params):
            self.severity_map = self._parse_severity_map(self.severity_map)

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
    def _severity_param(cls) -> Parameters:
        return Parameters(
            "severity_map",
            dict,
            False,
            "Minimum rule level for each severity band",
            dict(cls.DEFAULT_SEVERITY_MAP),
        )

    @classmethod
    def _alternative_template(cls) -> str:
        return DEFAULT_TEMPLATE
