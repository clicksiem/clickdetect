from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from logging import getLogger
from ..detector.runner import get_runner_instance
from .errors import runner_error

router = APIRouter(prefix="/plugins")

logger = getLogger(__name__)


@router.post("", status_code=201)
async def createPlugin(data: Dict[str, Any]):
    logger.info("createPlugin")
    plugin_id = data.get("id")
    if not plugin_id:
        raise HTTPException(status_code=422, detail="Required param not provided: id")
    runner = get_runner_instance()
    try:
        await runner.add_plugin(plugin_id, data.get("config"))
    except Exception as ex:
        raise runner_error(ex)
    return {"id": plugin_id}
