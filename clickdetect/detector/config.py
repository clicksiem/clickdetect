from asyncio import Lock
import colorlog
from importlib.metadata import version as get_version

_lock = Lock()
running = True
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


async def is_running():
    global running
    async with _lock:
        return running


async def stop_running():
    global running
    async with _lock:
        running = False


app_name = "clickdetect"
default_runner = "runner.yml"
default_port = 8080
version = get_version(app_name)
