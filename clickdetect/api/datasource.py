from typing import Any, Dict
from fastapi import APIRouter
from logging import getLogger
from ..detector.runner import get_runner_instance
from .errors import runner_error

router = APIRouter(prefix="/datasource")

logger = getLogger(__name__)


@router.post("", status_code=201)
async def createDatasource(data: Dict[str, Any]):
    logger.info("createDatasource")
    runner = get_runner_instance()
    try:
        datasource = await runner.add_datasource(data)
    except Exception as ex:
        raise runner_error(ex)
    return datasource.to_dict()
