from clickdetect.detector.manager import set_manager_instance, Manager
import asyncio
import uvicorn
import argparse
from typing import Any
from logging import getLogger
from fastapi import FastAPI
from os.path import exists as f_exists
from yaml import safe_load
from .api.detector import router as detector_router
from .api.rules import router as rules_router
from .detector.runner import Runner
from .detector.config import version
from .detector import config
from .detector.datasource import datasources
from .detector.webhooks import webhooks
from .detector.plugin import PluginSystem

logger = getLogger(__name__)

async def printPlugins():
    config.disableLogging()
    set_manager_instance(Manager())
    psys = PluginSystem()
    print('Loading plugins')
    await psys.load()
    for plugin in psys.plugins:
        print(f'Id: {plugin.id}')
        print(f'\tName: {plugin.name}')
        print(f'\tVersion: {plugin.version}')
        print()
    exit(0)

def printWebhooks():
    for w in webhooks:
        print(f"Webhook: {w._name()}")
        for param in w._params():
            print(
                f"\tName: {param.name}({param.type.__name__}) {'Required' if param.required else 'Optional'}. {f'Help: {param.help}' if param.help else ''}",
                end=" ",
            )
            if not param.required:
                print(f" Default: {param.default!r}")
            else:
                print()
        print("\n")
    exit(0)


def printDatasources():
    for ds in datasources:
        print(f"Datasources: {ds._name()}")
        for param in ds._params():
            print(
                f"\tName: {param.name}({param.type.__name__}) {'Required' if param.required else 'Optional'}. {f'Help: {param.help}' if param.help else ''}",
                end=" ",
            )
            if not param.required:
                print(f" Default: {param.default!r}")
            else:
                print()
        print("\n")
    exit(0)


async def load_api(args: Any):
    app = FastAPI(title=config.app_name)
    app.include_router(detector_router)
    app.include_router(rules_router)

    log_level = "info" if not args.verbose else "debug"
    server_config = uvicorn.Config(
        app, host="0.0.0.0", port=args.port, log_level=log_level
    )
    server = uvicorn.Server(server_config)
    await server.serve()


async def load_runner(args: Any) -> Runner | None:
    if args.stdin:
        data = safe_load(read_stdin())
    else:
        with open(args.runner, "r") as f:
            data = safe_load(f)

    if not data:
        logger.fatal("Invalid runner. The loaded runner is not a valid yaml")
        exit(1)

    runner = await Runner(data).init()
    if not runner:
        logger.warning("Runner not loaded")
        return None

    if not await runner.get_detectors():
        logger.error("No detector found")
        return None

    await runner.start_detectors(not args.no_start)
    return runner


async def loop_run(runner: Runner | None = None):
    try:
        while await config.is_running():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.warning("received kill event")
    except KeyboardInterrupt:
        logger.warning("Ctrl + c, killing")
    finally:
        if runner:
            await runner.manager.shutdown()
            await runner.close()


def read_stdin() -> str:
    from sys import stdin

    user_input = stdin.read()
    logger.debug(user_input)
    return user_input


async def main():
    parser = argparse.ArgumentParser(
        description=f"{config.app_name} is a tool to detect patterns and alerts in clickhouse and others database"
    )
    parser.add_argument(
        "--api",
        required=False,
        default=False,
        action="store_true",
        help="Enable api, required for clicksiem-backend",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=config.default_port,
        type=int,
        help=f"specify api port, default: {config.default_port}",
    )
    parser.add_argument(
        "-r",
        "--runner",
        default=config.default_runner,
        type=str,
        help=f"Runner file containing webhook, datasources, detectors and rules. Default: {config.default_runner}",
    )
    parser.add_argument(
        "--stdin", default=False, action="store_true", help="Read file from stdin"
    )
    parser.add_argument(
        "--version", default=False, action="store_true", help="Project version"
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true", help="Add verbosity"
    )
    parser.add_argument(
        "--reload",
        default=False,
        action="store_true",
        help="Watch rule files and reload on changes",
    )
    parser.add_argument(
        "--no-start",
        default=False,
        action="store_true",
        help="Do not start detectors on start",
    )
    parser.add_argument(
        "--list-webhooks", default=False, action="store_true", help="List all webhooks"
    )
    parser.add_argument(
        "--list-datasources",
        default=False,
        action="store_true",
        help="List all datasources",
    )
    parser.add_argument(
        '--list-plugins',
        default=False,
        action='store_true',
        help="List all plugins"
    )

    args = parser.parse_args()

    if args.version:
        print(version)
        exit(0)

    if args.list_webhooks:
        printWebhooks()

    if args.list_datasources:
        printDatasources()

    if args.list_plugins:
        await printPlugins()

    config.logConfig(verbose=args.verbose)
    logger = getLogger(__name__)

    if not f_exists(args.runner) and not args.stdin:
        logger.fatal(f"File {args.runner} does not exists")
        exit(1)

    runner = await load_runner(args)
    tasks = [loop_run(runner)]
    if args.api:
        tasks.append(load_api(args))
    if args.reload and runner:
        tasks.append(runner.start_watcher())
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    except Exception as ex:
        logger.error(f'Exception: {str(ex)}')


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
