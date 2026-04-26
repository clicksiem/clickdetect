import logging
from typing import Any
from .base import PluginBase
from ..hooks import HookRegistry, EventEnum
from ..manager import Manager

logger = logging.getLogger(__name__)

class ClickAgenticLLM(PluginBase):
    id = "clickexample"
    name = "clickdetect plugin sample"
    version = "v0.0.1"

    async def run(self, config: Any):
        logger.info("example plugin")
        logger.info(config)

    async def register_hooks(self, registry: HookRegistry) -> None:
        registry.register(EventEnum.on_rule_triggered, self._handle_rule_triggered)

    async def _handle_rule_triggered(
        self, rule, detector, result, template_data
    ) -> dict | None:
        logger.info(f'Rule: {rule}')
        logger.info(f'Detector: {detector}')
        logger.info(f'Result: {result}')
        logger.info(f'Template: {template_data}')

        return  {
            "template_data": { 
                **template_data,
                "example": {
                    "title": "this is an example plugin",
                }
            }
        }
