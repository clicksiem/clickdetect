from typing import Any, Dict
from fastapi import APIRouter
from logging import getLogger
from ..detector.runner import get_runner_instance
from .errors import runner_error

router = APIRouter(prefix="/webhooks")

logger = getLogger(__name__)


@router.post("", status_code=201)
async def createWebhook(data: Dict[str, Any]):
    logger.info("createWebhook")
    runner = get_runner_instance()
    try:
        webhook = await runner.add_webhook(data)
    except Exception as ex:
        raise runner_error(ex)
    # to_dict does not hide tokens, return only the name
    return {"name": webhook.name}
