from typing import Any, Dict
from ..manager import Manager
from ..hooks import HookRegistry

class PluginBase:
    id: str = 'plugin_id'
    name: str = 'plugin base'
    version: str = 'v0.0.1'
    manager: Manager
    active: bool

    def __init__(self, manager: Manager):
        self.manager = manager
        self.active = True

    async def run(self, config: Any):
        raise NotImplementedError('Plugin not implemented yet')

    async def register_hooks(self, registry: HookRegistry) -> None:
        pass

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version
        }
