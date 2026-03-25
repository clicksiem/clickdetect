from typing import List
from pathlib import Path
from watchfiles import awatch, Change
from logging import getLogger
from .detector import Detector

logger = getLogger(__name__)


class RuleWatcher:
    def __init__(self, detectors: List[Detector]):
        self.detectors = detectors

    def collect_base_dir(self, path: str) -> str:
        parts = Path(path).parts
        base_parts = []
        for part in parts:
            if any(c in part for c in ('*', '?', '[')):
                break
            base_parts.append(part)
        if not base_parts:
            return '.'
        return str(Path(*base_parts))

    async def start_watch(self):
        watch_paths: set[str] = set()
        for detector in self.detectors:
            if not detector.active:
                continue
            for rule_path in detector.rules:
                base_path = self.collect_base_dir(rule_path)
                watch_paths.add(base_path)

        if not watch_paths:
            logger.warning("No paths to watch")
            return

        logger.info(f"Watching rule paths: {watch_paths}")

        async for changes in awatch(*watch_paths):
            for change, path in changes:
                if not (path.endswith('.yml') or path.endswith('.yaml')):
                    continue
                for detector in self.detectors:
                    if not detector.active:
                        continue
                    if not any(
                        Path(path).is_relative_to(self.collect_base_dir(rp))
                        for rp in detector.rules
                    ):
                        continue
                    if change == Change.added:
                        logger.info(f"Rule added: {path}")
                        await detector.add_rule_by_path(path)
                    elif change == Change.modified:
                        logger.info(f"Rule modified: {path}")
                        await detector.reload_rule_by_path(path)
                    elif change == Change.deleted:
                        logger.info(f"Rule deleted: {path}")
                        await detector.remove_rule_by_path(path)
