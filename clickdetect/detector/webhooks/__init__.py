from clickdetect.detector.webhooks.forgejo import ForgejoWebhook
from typing import List, Type
from .base import BaseWebhook
from .generic import GenericWebhook
from .teams import TeamsWebhook
from .email import EmailWebhook
#from .matrix import MatrixWebhook


webhooks: List[Type[BaseWebhook]] = [
    GenericWebhook,
    TeamsWebhook,
    EmailWebhook,
    ForgejoWebhook
    # MatrixWebhook,
]
