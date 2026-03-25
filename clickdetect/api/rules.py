from fastapi import APIRouter, HTTPException
from ..detector.manager import get_manager_instance

router = APIRouter(prefix="/rules")


@router.get("/{detector_id}")
async def listRules(detector_id: str):
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    return [x.to_dict() for x in detector._rules]


@router.get("/{detector_id}/{rule_id}")
async def getRuleById(detector_id: str, rule_id: str):
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    rule = await detector.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule.to_dict()


@router.get("/{detector_id}/{rule_id}/pause")
async def pauseRule(detector_id: str, rule_id: str):
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    ok = await detector.setRuleActive(rule_id, False)
    if not ok:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True}


@router.get("/{detector_id}/{rule_id}/resume")
async def resumeRule(detector_id: str, rule_id: str):
    manager = get_manager_instance()
    detector = await manager.get_detector_by_id(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    ok = await detector.setRuleActive(rule_id, True)
    if not ok:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"ok": True}
