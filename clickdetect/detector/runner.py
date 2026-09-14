from typing import Any, List, Self, Dict
from logging import getLogger
from yaml import safe_dump
from .datasource.base import BaseDataSource
from .datasource import datasources
from .detector import Detector
from .rules import Rule
from .manager import Manager, set_manager_instance
from .plugin import PluginSystem
from .webhooks.generic import GenericWebhook
from .webhooks import webhooks as w_webhooks
from .watcher import RuleWatcher

logger = getLogger(__name__)


class RunnerConflictError(Exception):
    pass


class Runner:
    plugins_config: List[Dict[str, Any]]

    def __init__(
        self, data: Any, all_is_sigma: bool = False, dry_run: bool = False
    ) -> None:
        self.data = data
        self.plugins_config = []
        self.all_is_sigma = all_is_sigma
        self._dry_run = dry_run
        self.datasource: BaseDataSource | None = None
        self.webhooks: List[GenericWebhook] | None = None
        self.detectors: List[Detector] = []

    async def init(self) -> Self:
        await self.load_runner()
        return self

    async def init_empty(self) -> Self:
        # api only mode: datasource, webhooks, detectors and plugins are added through the api
        self.manager = Manager()
        set_manager_instance(self.manager)
        self.redis_config = None
        self.max_detector_time = None
        self.plugin_system = await self.parse_plugins(None)
        return self

    async def load_runner(self):
        data = self.data
        self.manager = Manager()
        set_manager_instance(self.manager)
        self.redis_config = data.get("redis", None)
        self.max_detector_time = data.get("max_detector_time", None)
        self.datasource = await self.parse_datasource(data.get("datasource", None))
        self.webhooks = await self.parse_webhooks(data.get("webhooks", None))
        self.detectors = await self.parse_detectors(data.get("detectors", None))
        self.plugin_system = await self.parse_plugins(data.get("plugins", None))

        await self.load_detectors()
        await self.load_plugins()
        await self.load_datasource()

    async def load_plugins(self):
        for plugin in self.plugins_config:
            plugin_id = plugin.get("id", None)
            config = plugin.get("config", None)
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
            try:
                await detector.setup_store(self.redis_config)
            except Exception as ex:
                logger.error(
                    f"Error connecting store for detector {detector.name}: {str(ex)}"
                )
                exit(1)
            if detector.all_is_sigma:
                await detector.load_rules_directory()
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
                source = await self.parse_webhook(webhook_name, webhook)
                if not source:
                    continue

                webhook_list.append(source)
            except Exception as ex:
                logger.error(f"Error loading webhook: {webhook_name}")
                logger.error(str(ex))
                continue
        logger.debug(f"webhook list: {webhook_list}")
        return webhook_list

    async def parse_webhook(self, name: str, webhook: Any) -> GenericWebhook | None:
        webhook_type = webhook.get("type", "generic")
        source = next((_w() for _w in w_webhooks if _w._name() == webhook_type), None)

        if not source:
            logger.error(f"Webhook not found: {webhook_type}")
            return None

        logger.info(f"Webhook {webhook_type}")

        await source._parse({**webhook, "name": name})
        return source

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
                all_is_sigma=detector.get("sigma", False),
                max_detector_time=self.max_detector_time,
                _dry_run=self._dry_run,
            )
            if self.all_is_sigma:
                await detector_obj.setAllIsSigma(True)
            if not detector_obj.all_is_sigma:
                await detector_obj.load_rules_directory()
            detectors_list.append(detector_obj)
        return detectors_list

    async def parse_plugins(self, plugins_config: Any) -> PluginSystem:
        plugin_system = PluginSystem()
        await plugin_system.load()

        if not plugins_config:
            logger.info("No plugins configured")
            return plugin_system

        for plugin_id, config in plugins_config.items():
            self.plugins_config.append({"id": plugin_id, "config": config})

        return plugin_system

    async def add_datasource(self, data: Any) -> BaseDataSource:
        if self.datasource:
            raise RunnerConflictError("Datasource already configured")
        datasource = await self.parse_datasource(data)
        await datasource.connect()
        self.datasource = datasource
        return datasource

    async def add_webhook(self, data: Any) -> GenericWebhook:
        name = data.get("name")
        if not name:
            raise ValueError("Required param not provided: name")
        if any(w.name == name for w in self.webhooks or []):
            raise RunnerConflictError(f"Webhook {name} already exists")

        webhook = await self.parse_webhook(name, data)
        if not webhook:
            raise LookupError(f"Webhook not found: {data.get('type', 'generic')}")
        # fail on template syntax errors now instead of on the first alert
        webhook.jinja_env.parse(webhook.template)
        await webhook.connect()

        self.webhooks = [*(self.webhooks or []), webhook]
        for detector in self.detectors:
            if name in (detector.webhooks or []):
                detector._webhooks.append(webhook)
        return webhook

    async def add_plugin(self, plugin_id: str, config: Any):
        if any(p.get("id") == plugin_id for p in self.plugins_config):
            raise RunnerConflictError(f"Plugin {plugin_id} already loaded")
        if not any(p.id == plugin_id for p in self.plugin_system.plugins):
            raise LookupError(f"Plugin {plugin_id} not found")
        if not await self.plugin_system.load_plugin_id(plugin_id, config):
            raise RuntimeError(f"Plugin {plugin_id} load error")
        self.plugins_config.append({"id": plugin_id, "config": config})

    async def add_detector(self, data: Any, auto_start: bool = True) -> str:
        if not self.datasource:
            raise RunnerConflictError("Datasource not configured")
        for required in ("name", "for"):
            if not data.get(required):
                raise ValueError(f"Required param not provided: {required}")

        data = {
            **data,
            "rules": data.get("rules") or [],
            "webhooks": data.get("webhooks") or [],
        }
        detector = (await self.parse_detectors({data["name"]: data}))[0]
        detector.datasource = self.datasource
        await detector.setup_store(self.redis_config)
        if detector.all_is_sigma:
            await detector.load_rules_directory()
        detector._hooks = self.plugin_system.hooks
        for webhook in self.webhooks or []:
            if webhook.name in (detector.webhooks or []):
                detector._webhooks.append(webhook)

        # the manager skips inactive detectors, schedule and pause it right away
        # so it stays reachable through the api
        active = detector.active
        detector.active = True
        job = await self.manager.run_detector(detector, auto_start and active)
        if not job:
            raise RuntimeError(f"Detector {detector.name} not scheduled")
        job_id = str(job.id)
        if not active:
            await self.manager.stop_scheduler(job_id)

        self.detectors.append(detector)
        return job_id

    async def add_rule(self, detector: Detector, data: Any) -> Rule:
        if await detector.get_rule_by_id(data.get("id")):
            raise RunnerConflictError(f"Rule {data.get('id')} already exists")
        rule = await detector.load_rule_buffer(data, safe_dump(data))
        if not rule:
            raise ValueError("Invalid rule format")
        if not detector.all_is_sigma:
            rule.rule = detector.datasource.parse_sigma(rule)
        await detector.add_rule(rule)
        return rule

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
        for detector in self.detectors:
            await detector.store.close()


_runner: Runner | None = None


def set_runner_instance(r: Runner) -> None:
    global _runner
    _runner = r


def get_runner_instance() -> Runner:
    if not _runner:
        raise RuntimeError("Runner not initialized")
    return _runner
