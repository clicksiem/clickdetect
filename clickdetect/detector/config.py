import colorlog
import logging
from asyncio import Lock
from importlib.metadata import version as get_version

_lock = Lock()
running = True
dry_run_code: int = 0
rule_eval_semaphore = 7
webhook_send_semaphore = 7


def logConfig(verbose: bool = False):
    level = colorlog.DEBUG if verbose else colorlog.INFO
    colorlog.basicConfig(
        level=level,
        format="%(asctime)s | %(log_color)s%(levelname)-8s%(reset)s | %(name)s | %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        force=True,
    )
def disableLogging():
    logging.disable(logging.ERROR)
    logging.disable(logging.CRITICAL)


async def is_running():
    global running
    async with _lock:
        return running


async def stop_running(code: int = 0):
    global running, dry_run_code
    async with _lock:
        if not running:  # already stopping: keep the first code
            return
        dry_run_code = code
        running = False


app_name = "clickdetect"
default_runner = "runner.yml"
default_port = 8080
version = get_version(app_name)
