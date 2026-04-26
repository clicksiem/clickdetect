import logging
from typing import Dict
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from .utils import parse_interval_to_seconds
from .detector import Detector

logger = logging.getLogger(__name__)


class Manager:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.job_detectors: Dict[str, Detector] = {}

    async def run_detector(
        self, detector: Detector, auto_start: bool = True
    ) -> Job | None:
        logger.info("creating new scheduler")

        if not detector.active:
            logger.debug(f"detector {detector.name} not active")
            return None

        sec = parse_interval_to_seconds(detector.for_time)
        if auto_start:
            job = self.scheduler.add_job(
                detector.callback, "interval", seconds=sec, next_run_time=datetime.now()
            )
        else:
            job = self.scheduler.add_job(detector.callback, "interval", seconds=sec)

        detector._next_time = job.next_run_time.timestamp()
        self.job_detectors[str(job.id)] = detector

        logger.debug(f"New job id: {job.id}")
        return job

    async def stop_scheduler(self, job_id: str):
        logger.info(f"stopping scheduler: {job_id}")
        detector = self.job_detectors.get(job_id)
        if not detector:
            return None
        await detector.setActive(False)
        self.scheduler.pause_job(job_id)
        return True

    async def remove_scheduler(self, job_id: str):
        logger.info(f"removing scheduler: {job_id}")
        detector = self.job_detectors.get(job_id)
        if not detector:
            return None
        self.scheduler.remove_job(job_id)
        return True

    async def resume_scheduler(self, job_id: str):
        logger.info(f"resuming scheduler: {job_id}")
        detector = self.job_detectors.get(job_id)
        if not detector:
            return None
        self.scheduler.resume_job(job_id)
        return True

    async def get_detectors(self) -> Dict[str, Detector]:
        return self.job_detectors

    async def get_detector_by_id(self, id: str) -> Detector | None:
        return self.job_detectors.get(id)

    async def shutdown(self, wait: bool = True):
        self.scheduler.shutdown(wait=wait)


_manager: Manager | None = None


def set_manager_instance(m: Manager) -> None:
    global _manager
    _manager = m


def get_manager_instance() -> Manager:
    if not _manager:
        raise RuntimeError("Manager not initialized")
    return _manager

