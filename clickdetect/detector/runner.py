from typing import Any, List, Self, Dict
from logging import getLogger
from .datasource.base import BaseDataSource
from .datasource import datasources
from .detector import Detector
from .manager import Manager, set_manager_instance
from .plugin import PluginSystem
from .webhooks.generic import GenericWebhook
from .webhooks import webhooks as w_webhooks
from .watcher import RuleWatcher
logger = getLogger(__name__)


class Runner:
    plugins_config: List[Dict[str, Any]]
    def __init__(self, data: Any) -> None:
        self.data = data
        self.plugins_config = []

    async def init(self) -> Self:
        await self.load_runner()
        return self

    async def load_runner(self):
        data = self.data
        self.manager = Manager()
        set_manager_instance(self.manager)
        self.datasource = await self.parse_datasource(data.get("datasource", None))
        self.webhooks = await self.parse_webhooks(data.get("webhooks", None))
        self.detectors = await self.parse_detectors(data.get("detectors", None))
        self.plugin_system = await self.parse_plugins(data.get("plugins", None))

        await self.load_detectors()
        await self.load_plugins()
        await self.load_datasource()


    async def load_plugins(self):
        for plugin in self.plugins_config:
            plugin_id = plugin.get('id', None)
            config = plugin.get('config', None)
            if not plugin_id:
                continue
            await self.plugin_system.load_plugin_id(plugin_id, config)

    async def load_datasource(self):
        logger.info("Connecting in datasource")
        try:
            await self.datasource.connect()
        except Exception as ex:
            logger.error(
                f"Error connecting in datasource: {self.datasource._name()} | {str(ex)}"
            )
            exit(1)

    async def load_detectors(self):
        logger.info("loading detectors")
        for detector in self.detectors:
            detector.datasource = self.datasource
            detector._hooks = self.plugin_system.hooks
            if self.webhooks:
                for webhook in self.webhooks:
                    if webhook.name in detector.webhooks:
                        try:
                            await webhook.connect()
                        except Exception as ex:
                            logger.error(f"webhook error: {str(ex)}")
                        finally:
                            detector._webhooks.append(webhook)

    async def parse_datasource(self, datasource: Any) -> BaseDataSource:
        if not datasource:
            logger.fatal("No datasource found")
            raise Exception("No datasource config found")

        source_type = datasource.get("type", "clickhouse")
        logger.info(f"Datasource {source_type}")

        source = next((_s() for _s in datasources if _s._name() == source_type), None)

        if not source:
            raise ModuleNotFoundError("Datasource not found")

        await source._parse(datasource)
        return source

    async def parse_webhooks(self, webhooks: Any) -> List[GenericWebhook] | None:
        if not webhooks:
            logger.warning("No webhooks found in config")
            return
        logger.debug(f"Webhooks| {webhooks}")

        webhook_list = []
        for webhook_name, webhook in webhooks.items():
            try:
                webhook_type = webhook.get("type", "generic")
                source = next(
                    (_w() for _w in w_webhooks if _w._name() == webhook_type), None
                )

                if not source:
                    logger.error(f"Webhook not found: {webhook_type}")
                    continue

                logger.info(f"Webhook {webhook_type}")

                await source._parse({**webhook, "name": webhook_name})

                webhook_list.append(source)
            except Exception as ex:
                logger.error(f"Error loading webhook: {webhook_name}")
                logger.error(str(ex))
                continue
        logger.debug(f"webhook list: {webhook_list}")
        return webhook_list

    async def parse_detectors(self, detectors: Any) -> List[Detector]:
        if not detectors:
            logger.fatal("No detectors found")
            raise Exception("No detectors found")
        logger.debug(f"Detectors| {detectors}")

        detectors_list = []
        for _, detector in detectors.items():
            detector_obj = Detector(
                name=detector.get("name"),
                for_time=detector.get("for"),
                description=detector.get("description"),
                rules=detector.get("rules"),
                webhooks=detector.get("webhooks"),
                data=detector.get("data"),
                tenant=detector.get("tenant", "default"),
                active=detector.get("active", True),
            )
            await detector_obj.load_rules_directory()
            if not detector_obj._rules:
                continue
            detectors_list.append(detector_obj)
        return detectors_list

    async def parse_plugins(self, plugins_config: Any) -> PluginSystem:
        plugin_system = PluginSystem()
        await plugin_system.load()

        if not plugins_config:
            logger.info("No plugins configured")
            return plugin_system

        for plugin_id, config in plugins_config.items():
            self.plugins_config.append({ 'id': plugin_id, 'config': config })

        return plugin_system

    async def start_detectors(self, auto_start: bool = True):
        logger.info("scheduling detectors")
        for detector in self.detectors:
            await self.manager.run_detector(detector, auto_start)

    async def get_detectors(self):
        return self.detectors

    async def get_webhooks(self):
        return self.webhooks

    async def get_datasource(self):
        return self.datasource

    async def start_watcher(self):
        watcher = RuleWatcher(self.detectors)
        await watcher.start_watch()

    async def close(self):
        logger.info("Cleaning up resources...")
        if self.webhooks:
            for webhook in self.webhooks:
                await webhook.close()
