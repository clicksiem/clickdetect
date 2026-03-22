from typing import Tuple
from dataclasses import dataclass, field
from typing import Any, List
from glob import glob
from json import dumps
from yaml import safe_load
from logging import getLogger
from datetime import datetime, timedelta
from asyncio import create_task, Semaphore, gather, Lock as a_lock
from jinja2 import Environment
from .webhooks.base import BaseWebhook
from .datasource.base import DataSourceQueryResult, BaseDataSource
from .rules import Rule
from . import utils
from . import config

logger = getLogger(__name__)


@dataclass
class Detector:
    name: str
    for_time: str
    description: str
    rules: List[str] = field(default_factory=list)
    webhooks: List[str] = field(default_factory=list)
    data: Any = field(default_factory=dict)
    tenant: str = field(default="default")
    active: bool = field(default=True)

    datasource: BaseDataSource = field(init=False)
    _rules: List[Rule] = field(default_factory=list)
    _webhooks: List[BaseWebhook] = field(default_factory=list)
    _last_time: float = field(default_factory=float)
    _next_time: float = field(default_factory=float)
    _rule_lock: a_lock = field(default_factory=a_lock)
    _callback_rule_lock: a_lock = field(default_factory=a_lock)
    _webhook_sem: Semaphore = field(default_factory=Semaphore)
    _rule_eval_sem: Semaphore = field(default_factory=Semaphore)
    jinja_env: Environment = field(default_factory=Environment)

    def __post_init__(self):
        for_time_seconds = utils.parse_interval_to_seconds(self.for_time)
        self.for_time_seconds = for_time_seconds
        self._last_time = (
            datetime.now() - timedelta(seconds=for_time_seconds)
        ).timestamp()
        self._next_time = (datetime.now()).timestamp()

        logger.debug(
            f"__post_init__ | for_time: {self.for_time} | interval_seconds: {for_time_seconds} | _last_time: {self._last_time}"
        )

        logger.debug("Setup jinja template environment")
        self.jinja_env = Environment()
        self.jinja_env.filters["to_list_like"] = lambda x: ", ".join(
            f"'{i}'" for i in x
        )  # '1', '2', '3'
        self.jinja_env.filters["to_list"] = lambda x: ", ".join(
            str(i) for i in x
        )  # 1, 2, 3
        self.jinja_env.filters["tojson"] = lambda x: dumps(
            x, default=utils.json_serializer
        )

        self._rule_lock = a_lock()
        self._callback_rule_lock = a_lock()
        self._rule_eval_sem = Semaphore(config.rule_eval_semaphore)
        self._webhook_sem = Semaphore(config.webhook_send_semaphore)

    async def call_webhook(
        self, rule: Rule, value: DataSourceQueryResult, time: Tuple[float, float]
    ):
        value.datasource = self.datasource._name()
        startime, endtime = time
        async with self._webhook_sem:
            for webhook in self._webhooks:
                try:
                    template_data = {
                        "rule": rule.to_dict(),
                        "data": value.to_dict(),
                        "detector": self.to_dict(),
                        "datasource": self.datasource.to_dict(),
                        "time": {"startime": startime, "endtime": endtime},
                    }
                    template = self.jinja_env.from_string(webhook.template).render(
                        **template_data
                    )
                    await webhook.send(template, template_data)
                except Exception as ex:
                    logger.error(
                        f"Cant send alert to webhook: {webhook._name()} | Exception: {str(ex)}"
                    )

    async def evaluate_rule(self, rule: Rule, startime: float, endtime: float):
        async with self._rule_eval_sem:
            try:
                diff = endtime - startime
                logger.debug(
                    f"startime: {startime} | endtime: {endtime} | seconds: {diff:.3f}s"
                )

                template = self.jinja_env.from_string(rule.rule)
                query = template.render(
                    startime=str(int(startime)),
                    endtime=str(int(endtime)),
                    interval=self.for_time,
                    rule=rule,
                    rule_id=rule.id,
                    rule_level=rule.level,
                    rule_group=rule.group,
                    datasource=self.datasource.to_dict(),
                    data=rule.data,
                    detector=self,
                )

                logger.debug(f"Rule id: {rule.id}")
                logger.debug(f"Rule name: {rule.name}")
                logger.debug(f"rule query:\n {query}\n")
                result = await self.datasource.query(query)

                if result is None:
                    logger.warning("Datasource unavailable, skipping rule evaluation")
                    return

                if rule.verify_condition(result.len):
                    logger.info(f"Rule triggered | ID: {rule.id} | Name: {rule.name}")
                    create_task(self.call_webhook(rule, result, (startime, endtime)))
                else:
                    logger.debug(
                        f"Rule not triggered | ID: {rule.id} | Name: {rule.name}"
                    )

            except Exception as ex:
                logger.error(
                    f"Unhandled exception: Rule id: {rule.id} | Exception: {str(ex)}"
                )

    async def callback(self):
        if not await config.is_running():
            logger.debug(f"Canceling Detector {self.name} callback")
            return

        logger.debug(f"Running detector {self.name} | Rules: {self._rules.__len__()}")

        endtime = datetime.now().timestamp()
        startime = self._last_time
        self._last_time = endtime
        self._next_time = endtime + self.for_time_seconds

        async with self._callback_rule_lock:
            rules_snapshot = self._rules.copy()

        await gather(
            *[
                self.evaluate_rule(rule, startime, endtime)
                for rule in rules_snapshot
                if rule.active
            ]
        )

    async def get_rule_by_id(self, id: str):
        async with self._rule_lock:
            r = next((x for x in self._rules if x.id == id), None)
            return r

    async def remove_rule_by_id(self, id: str):
        async with self._rule_lock:
            r = next((r for r in self._rules if r.id == id), None)
            if r:
                self._rules.remove(r)

    async def add_rule(self, rule: Rule):
        async with self._rule_lock:
            if any(r.id == rule.id for r in self._rules):
                logger.error(f"The rule {rule.id} already exists")
                return None
            self._rules.append(rule)

    async def setRuleActive(self, rule_id: str, active: bool):
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return None
        async with self._rule_lock:
            rule.active = active

    async def load_rule_buffer(self, rule: Any) -> Rule | None:
        rule_data = Rule(
            id=rule.get("id"),
            name=rule.get("name"),
            level=rule.get("level"),
            size=rule.get("size", ">0"),  # default >0
            active=rule.get("active", True),  # default is True
            rule=rule.get("rule"),
            author=rule.get("author", []),
            group=rule.get("group", ""),
            tags=rule.get("tags", []),
            data=rule.get("data", {}),
            description=rule.get("description", ""),
            path="",
        )

        if (
            not rule_data.id
            or not rule_data.name
            or not rule_data.size
            or not rule_data.rule
        ):
            logger.error("Invalid rule format")
            return None

        rule_data.detector = self.data

        logger.debug(f"Rule | {rule_data}")
        return rule_data

    async def load_rule_path(self, rule_path: str) -> Rule | None:
        logger.info(f"Loading rule: {rule_path}")
        try:
            with open(rule_path, "r") as f:
                data = safe_load(f)
            rule_loaded = await self.load_rule_buffer(data)
            if not rule_loaded:
                raise Exception("Rule not loaded")
            rule_loaded.path = rule_path
            return rule_loaded
        except (FileNotFoundError, FileExistsError):
            logger.error("Rule file does not exists")
            return None
        except Exception as ex:
            logger.error(f"Error in rule loading: {ex}")
            return None

    async def load_rules_directory(self) -> List[Rule]:
        logger.debug("finding rules")
        for rule in self.rules:
            rules_in_path = glob(rule, recursive=True)
            for rule_path in rules_in_path:
                if rule_path.endswith(".yml") or rule_path.endswith(".yaml"):
                    if r := await self.load_rule_path(rule_path):
                        await self.add_rule(r)
        return self._rules

    async def setActive(self, active: bool):
        self.active = active

    def to_dict(self):
        return {
            "name": self.name,
            "for_time": self.for_time,
            "description": self.description,
            "rules": self.rules,
            "webhooks": self.webhooks,
            "data": self.data,
            "tenant": self.tenant,
            "active": self.active,
            "datasource": self.datasource.to_dict(),
        }
