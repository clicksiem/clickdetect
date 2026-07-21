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
    sigma: bool = field(default=False)

    operators: ClassVar[Dict[str, Callable[[int, int], bool]]] = {
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
    }

    MIN_LEVEL: ClassVar[int] = 0
    MAX_LEVEL: ClassVar[int] = 100

    # sigma rules carry `level` as a string, map it into the clickdetect scale
    sigma_levels: ClassVar[Dict[str, int]] = {
        "informational": 10,
        "low": 30,
        "medium": 50,
        "high": 75,
        "critical": 90,
    }

    def __post_init__(self):
        pattern = r"^(>=|<=|==|>|<)\s*(\d+)$"
        match = re.match(pattern, self.size.strip())

        if not match:
            logger.error(f"Invalid rule condition: {self.size}")
            raise ValueError(f"Invalid rule condition: {self.size}")

        self.condition_operator = match.group(1)
        self.condition_value = int(match.group(2))
        self.level = self._parse_level(self.level)

    @classmethod
    def _parse_level(cls, level: Any) -> int:
        if isinstance(level, str) and not level.strip().lstrip("-").isdigit():
            value = cls.sigma_levels.get(level.strip().lower())
            if value is None:
                logger.error(f"Invalid rule level: {level}")
                raise ValueError(f"Invalid rule level: {level}")
            return value

        try:
            value = int(level)
        except (TypeError, ValueError):
            logger.error(f"Invalid rule level: {level}")
            raise ValueError(f"Invalid rule level: {level}")

        if not cls.MIN_LEVEL <= value <= cls.MAX_LEVEL:
            logger.error(f"Rule level out of range: {value}")
            raise ValueError(
                f"Rule level must be between {cls.MIN_LEVEL} and {cls.MAX_LEVEL}: {value}"
            )

        return value

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
            "sigma": self.sigma
        }
