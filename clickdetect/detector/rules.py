from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, List
from logging import getLogger
import re

logger = getLogger(__name__)


@dataclass
class Rule:
    id: str
    name: str
    level: int
    size: str
    active: bool
    rule: str
    author: List[str] = field(default_factory=list)
    group: str = field(default_factory=str)
    tags: List[str] = field(default_factory=list)
    data: Any = field(default=None)
    description: str = field(default="")
    detector: Any = field(default=None)
    path: str = field(default="")

    operators: ClassVar[Dict[str, Callable[[int, int], bool]]] = {
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
    }

    def __post_init__(self):
        pattern = r"^(>=|<=|==|>|<)\s*(\d+)$"
        match = re.match(pattern, self.size.strip())

        if not match:
            logger.error(f"Invalid rule condition: {self.size}")
            raise ValueError(f"Invalid rule condition: {self.size}")

        self.condition_operator = match.group(1)
        self.condition_value = int(match.group(2))

    def verify_condition(self, value: int) -> bool:
        logger.debug(f"verify_condition: {value} {self.size}")
        return self.operators[self.condition_operator](value, self.condition_value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "size": self.size,
            "active": self.active,
            "rule": self.rule,
            "author": self.author,
            "group": self.group,
            "tags": self.tags,
            "data": self.data,
            "description": self.description,
            "detector": self.detector,
            "path": self.path,
        }
