from fastapi import APIRouter, HTTPException
from ..detector.manager import get_manager_instance
from ..detector.detector import Detector
from datetime import datetime

router = APIRouter(prefix='/detector')

def detector_to_dict(job_id: str, d: Detector):
    return {
        'id': job_id,
        'name': d.name,
        'description': d.description,
        'tenant': d.tenant,
        'active': d.active,
        'for_time': d.for_time,
        'rules_count': len(d._rules),
        'webhooks': d.webhooks,
        'last_time_exec': datetime.fromtimestamp(d._last_time).isoformat(),
        'next_time_exec': datetime.fromtimestamp(d._next_time).isoformat()
    }


@router.get('/list')
async def listDetectors():
    manager = get_manager_instance()
    detectors = await manager.get_detectors()
    return [detector_to_dict(job_id, d) for job_id, d in detectors.items()]


@router.get('/tenant/{tenant}')
async def getDetectorsByTenant(tenant: str):
    manager = get_manager_instance()
    detectors = await manager.get_detectors()
    return [detector_to_dict(job_id, d) for job_id, d in detectors.items() if d.tenant == tenant]


@router.get('/{id}')
async def getDetector(id: str):
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(id)
    if not detector:
        raise HTTPException(status_code=404, detail='Detector not found')
    return detector_to_dict(id, detector)


@router.delete('/{id}')
async def deleteDetector(id: str):
    manager = get_manager_instance()
    result = await manager.remove_scheduler(id)
    if not result:
        raise HTTPException(status_code=404, detail='Detector not found')
    return {'deleted': id}


@router.post('/{id}/stop')
async def stopDetector(id: str):
    manager = get_manager_instance()
    result = await manager.stop_scheduler(id)
    if not result:
        raise HTTPException(status_code=404, detail='Detector not found')
    return {'stopped': id}


@router.post('/{id}/resume')
async def resumeDetector(id: str):
    manager = get_manager_instance()
    result = await manager.resume_scheduler(id)
    if not result:
        raise HTTPException(status_code=404, detail='Detector not found')
    return {'resumed': id}
