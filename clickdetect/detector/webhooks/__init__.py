from typing import List, Type
from .discord import DiscordWebhook
from .base import BaseWebhook
from .telegram import TelegramWebhook
from .forgejo import ForgejoWebhook
from .generic import GenericWebhook
from .teams import TeamsWebhook
from .email import EmailWebhook
from .iris import DfirIRISWebhook
from .slack import SlackWebhook
# from .matrix import MatrixWebhook


webhooks: List[Type[BaseWebhook]] = [
    GenericWebhook,
    TeamsWebhook,
    EmailWebhook,
    ForgejoWebhook,
    DfirIRISWebhook,
    SlackWebhook,
    TelegramWebhook,
    DiscordWebhook,
    # MatrixWebhook,
]
