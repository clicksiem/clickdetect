from fastapi import HTTPException
from jinja2 import TemplateSyntaxError
from logging import getLogger
from ..detector.runner import RunnerConflictError

logger = getLogger(__name__)


def runner_error(ex: Exception, default_status: int = 502) -> HTTPException:
    if isinstance(ex, RunnerConflictError):
        status = 409
    elif isinstance(ex, (LookupError, ModuleNotFoundError)):
        status = 404
    elif isinstance(ex, (ValueError, TemplateSyntaxError)):
        status = 422
    else:
        status = default_status
    logger.error(f"{status} | {str(ex)}")
    return HTTPException(status_code=status, detail=str(ex))
