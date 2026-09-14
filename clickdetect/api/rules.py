from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from ..detector.manager import get_manager_instance
from ..detector.runner import get_runner_instance
from .errors import runner_error

router = APIRouter(prefix="/rules")

from logging import getLogger

logger = getLogger(__name__)

@router.post("/{detector_id}", status_code=201)
async def createRule(detector_id: str, data: Dict[str, Any]):
    logger.info('createRule')
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        logger.error(f'Detector {detector_id} not found')
        raise HTTPException(status_code=404, detail="Detector not found")
    runner = get_runner_instance()
    try:
        rule = await runner.add_rule(detector, data)
    except Exception as ex:
        # no network involved, any other failure is an invalid rule (e.g. sigma conversion)
        raise runner_error(ex, default_status=422)
    return rule.to_dict()


@router.get("/{detector_id}")
async def listRules(detector_id: str):
    logger.info('listRules')
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        logger.error(f'Detector {detector_id} not found')
        raise HTTPException(status_code=404, detail="Detector not found")
    rules = [x.to_dict() for x in detector._rules]
    logger.debug(f'Detector {detector_id} Rules:\n{rules}')
    return rules


@router.get("/{detector_id}/{rule_id}")
async def getRuleById(detector_id: str, rule_id: str):
    logger.info('getRuleById')
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        logger.error(f'Detector {detector_id} not found')
        raise HTTPException(status_code=404, detail="Detector not found")
    rule = await detector.get_rule_by_id(rule_id)
    if not rule:
        logger.error(f'Rule {rule_id} not found')
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule.to_dict()


@router.get("/{detector_id}/{rule_id}/pause")
async def pauseRule(detector_id: str, rule_id: str):
    logger.info('pauseRule')
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        logger.error(f'Detector {detector_id} not found')
        raise HTTPException(status_code=404, detail="Detector not found")
    ok = await detector.setRuleActive(rule_id, False)
    if not ok:
        logger.error(f'Rule {rule_id} not found')
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True}


@router.get("/{detector_id}/{rule_id}/resume")
async def resumeRule(detector_id: str, rule_id: str):
    logger.info(f'resumeRule detector: {detector_id} | rule: {rule_id}')
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        logger.error(f'Detector {detector_id} not found')
        raise HTTPException(status_code=404, detail="Detector not found")
    ok = await detector.setRuleActive(rule_id, True)
    if not ok:
        logger.error(f'Rule {rule_id} not found')
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True}
