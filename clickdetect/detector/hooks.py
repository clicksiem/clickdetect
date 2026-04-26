from enum import Enum
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

class EventEnum(Enum):
    on_rule_triggered = 'on_rule_triggered'

class HookRegistry:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

    def register(self, event: EventEnum, handler: Callable) -> None:
        self._handlers[event.value].append(handler)

    async def emit(self, event: EventEnum, **kwargs: Any) -> Dict[str, Any]:
        for handler in self._handlers.get(event.value, []):
            try:
                result = await handler(**kwargs)
                if isinstance(result, dict):
                    kwargs.update(result)
            except Exception as ex:
                logger.error(f"Hook error [{event.value}] {getattr(handler, '__qualname__', repr(handler))}: {ex}")
        return kwargs
