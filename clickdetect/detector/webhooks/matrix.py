import os
from typing import List
from logging import getLogger
from .. import config
from ..utils import machine_device_id, Parameters
from .base import BaseWebhook
from nio import AsyncClient, AsyncClientConfig

logger = getLogger(__name__)

# TODO: use aiohttp, nio is soo heavy for this project


class MatrixWebhook(BaseWebhook):
    name: str
    url: str
    username: str
    password: str
    room_id: str
    verify: bool
    timeout: int
    template: str
    client: AsyncClient

    async def close(self):
        await self.client.close()

    async def connect(self):
        os.makedirs("./matrix", exist_ok=True)

        matrix_config = AsyncClientConfig(store_sync_tokens=True)
        self.client = AsyncClient(
            self.url,
            self.username,
            device_id=machine_device_id(),
            store_path="./matrix",
            ssl=self.verify,
            config=matrix_config,
        )

        await self.client.login(self.password, device_name=config.app_name)
        await self.client.sync(timeout=10, full_state=True)

        logger.debug("Matrix client connected")

    async def send(self, data: str):
        try:
            if not self.client.logged_in:
                logger.error("Not logged in matrix")
                return

            logger.info(await self.client.list_direct_rooms())
            await self.client.room_send(
                room_id=self.room_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": data},
            )
        except Exception as ex:
            logger.error(f"Cant send matrix alert: {str(ex)}")
            pass

    @classmethod
    def _name(cls) -> str:
        return "matrix"

    @classmethod
    def _params(cls) -> List[Parameters]:
        return [
            Parameters('name', str, False, 'Webhook name'),
            Parameters('url', str, True, 'Matrix homeserver URL'),
            Parameters('username', str, True, 'Matrix username'),
            Parameters('password', str, True, 'Matrix password'),
            Parameters('room_id', str, True, 'Matrix room ID'),
            Parameters('verify', bool, False, 'SSL verify', True),
            Parameters('template', str, False, 'Message template', BaseWebhook._alternative_template()),
        ]
