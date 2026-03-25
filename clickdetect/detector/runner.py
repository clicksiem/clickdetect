from typing import Any, List, Self
from logging import getLogger
from .datasource.base import BaseDataSource
from .datasource import datasources
from .detector import Detector
from .webhooks.generic import GenericWebhook
from .webhooks import webhooks as w_webhooks
from .watcher import RuleWatcher
logger = getLogger(__name__)


class Runner:
    def __init__(self, data: Any) -> None:
        self.data = data

    async def init(self) -> Self:
        await self.load_runner()
        return self

    async def load_runner(self):
        data = self.data
        self.datasource = await self.parse_datasource(data.get("datasource", None))
        self.webhooks = await self.parse_webhooks(data.get("webhooks", None))
        self.detectors = await self.parse_detectors(data.get("detectors", None))

        logger.info("loading detectors")
        for detector in self.detectors:
            detector.datasource = self.datasource
            if self.webhooks:
                for webhook in self.webhooks:
                    if webhook.name in detector.webhooks:
                        try:
                            await webhook.connect()
                        except Exception as ex:
                            logger.error(f"webhook error: {str(ex)}")
                        finally:
                            detector._webhooks.append(webhook)

        logger.info("Connecting in datasource")
        try:
            await self.datasource.connect()
        except Exception as ex:
            logger.error(
                f"Error connecting in datasource: {self.datasource._name()} | {str(ex)}"
            )
            exit(1)

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
