from fastapi import APIRouter, HTTPException
from ..detector.manager import get_manager_instance
from ..detector.detector import Detector
from datetime import datetime
from logging import getLogger

router = APIRouter(prefix="/detector")

logger = getLogger(__name__)


def detector_to_dict(job_id: str, d: Detector):
    return {
        "id": job_id,
        "name": d.name,
        "description": d.description,
        "tenant": d.tenant,
        "active": d.active,
        "for_time": d.for_time,
        "rules_count": len(d._rules),
        "webhooks": d.webhooks,
        "last_time_exec": datetime.fromtimestamp(d._last_time).isoformat(),
        "next_time_exec": datetime.fromtimestamp(d._next_time).isoformat(),
    }


@router.get("/list")
async def listDetectors():
    logger.info("listDetectors")
    manager = get_manager_instance()
    detectors = await manager.get_detectors()
    detectors_list = [detector_to_dict(job_id, d) for job_id, d in detectors.items()]
    logger.debug(f"Detectors {detectors_list}")
    return detectors_list


@router.get("/tenant/{tenant}")
async def getDetectorsByTenant(tenant: str):
    logger.info("getDetectorsByTenant")
    manager = get_manager_instance()
    detectors = await manager.get_detectors()
    detectors_by_tenant = [
        detector_to_dict(job_id, d)
        for job_id, d in detectors.items()
        if d.tenant == tenant
    ]
    logger.debug(f"Detectors by tenant {tenant} {detectors_by_tenant}")
    return detectors_by_tenant


@router.get("/{id}")
async def getDetector(id: str):
    logger.info("getDetector")
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(id)
    if not detector:
        logger.error(f"Detector {id} not found")
        raise HTTPException(status_code=404, detail="Detector not found")
    logger.debug(f"Detector returned {id}")
    return detector_to_dict(id, detector)


@router.delete("/{id}")
async def deleteDetector(id: str):
    logger.info("deleteDetector")
    manager = get_manager_instance()
    result = await manager.remove_scheduler(id)
    if not result:
        logger.error(f"Detector {id} not found")
        raise HTTPException(status_code=404, detail="Detector not found")
    logger.debug(f"Detector deteled {id}")
    return {"deleted": id}


@router.post("/{id}/stop")
async def stopDetector(id: str):
    logger.info("stopDetector")
    manager = get_manager_instance()
    result = await manager.stop_scheduler(id)
    if not result:
        logger.error(f"Detector {id} not found")
        raise HTTPException(status_code=404, detail="Detector not found")
    logger.debug(f"detector stopped {id}")
    return {"stopped": id}


@router.post("/{id}/resume")
async def resumeDetector(id: str):
    logger.info("resumeDetector")
    manager = get_manager_instance()
    result = await manager.resume_scheduler(id)
    if not result:
        logger.error(f"Detector {id} not found")
        raise HTTPException(status_code=404, detail="Detector not found")
    logger.debug(f"detector stopped {id}")
    return {"resumed": id}
