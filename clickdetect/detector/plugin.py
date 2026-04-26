import logging
import importlib
import importlib.util
from typing import List, Any, Dict
from pathlib import Path
from .plugins.base import PluginBase
from ..detector.manager import get_manager_instance
from ..detector.manager import Manager
from .hooks import HookRegistry

BASE_DIR = Path(__file__).resolve().parent
PLUGINS_DIR = BASE_DIR / "plugins"

logger = logging.getLogger(__name__)

class PluginSystem:
    def __init__(self):
        self.plugins: List[PluginBase] = []
        self.loaded_plugins: List[PluginBase] = []
        self.manager: Manager = get_manager_instance()
        self.hooks: HookRegistry = HookRegistry()

    async def load_plugin_id(self, id: str, config: Any):
        logger.debug(f'Trying to load plugin {id}')
        logger.debug(f'config: {config}')

        r = next((x for x in self.plugins if x.id == id), None)
        if not r:
            logger.error(f'plugin id {id} not found')
            return None

        logger.info(f'plugin {r.id}:')
        logger.info(f'\tName: {r.name}')
        logger.info(f'\tVersion: {r.version}')

        try:
            await r.run(config)
            await r.register_hooks(self.hooks)
        except Exception as ex:
            logger.error('Plugin load error')
            logger.error(str(ex))

    async def load(self):
        logger.debug('Loading plugins')
        for file in PLUGINS_DIR.iterdir():
            if file.name.endswith(".py"):
                try:
                    logger.debug(f'trying to load module: {file}')
                    module = self.load_module_by_path(file)
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        if (
                            isinstance(obj, type)
                            and issubclass(obj, PluginBase)
                            and obj is not PluginBase
                        ):
                            logger.info(f'loading module: {file}')
                            self.plugins.append(obj(self.manager))
                except Exception as ex:
                    logger.error(f'failed to load module {file}')
                    logger.error(str(ex))

        return self.plugins

    def load_module_by_path(self, path: Path):
        module_name = f"clickdetect.detector.plugins.{path.stem}"
        return importlib.import_module(module_name)

    def to_dict(self) -> Dict:
        return {
            'plugins': [x.to_dict() for x in self.plugins]
        }
