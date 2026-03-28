import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from logging import getLogger
from .base import BaseWebhook, BaseWebhookParameters

logger = getLogger(__name__)

DEFAULT_TEMPLATE = """\
[ALERT] {{ rule.name }}
{% if rule.description %}
{{ rule.description }}
{% endif %}
Rule ID  : {{ rule.id }}
Level    : {{ rule.level }}
Group    : {{ rule.group or "-" }}
Tags     : {{ rule.tags | to_list or "-" }}
Author   : {{ rule.author | to_list or "-" }}
Detector : {{ detector.name }} (tenant: {{ detector.tenant }})
Interval : {{ detector.for_time }}
Matches  : {{ data.len }}
"""


class EmailWebhook(BaseWebhook):
    name: str
    host: str
    port: int
    username: str
    password: str
    from_addr: str
    to_addrs: List[str]
    use_tls: bool
    subject: str
    template: str
    params: List[BaseWebhookParameters] = []

    async def close(self):
        pass

    async def connect(self):
        pass

    async def send(self, data: str, template_data: Dict):
        try:
            subject = self.jinja_env.from_string(self.subject).render(**template_data)
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Subject"] = subject
            msg.attach(MIMEText(data, "plain"))

            logger.debug(f"Sending email alert to {self.to_addrs}")

            if self.use_tls:
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                    server.login(self.username, self.password)
                    server.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            else:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.from_addr, self.to_addrs, msg.as_string())

            logger.info(f"Email alert sent to {self.to_addrs}")

        except Exception as ex:
            logger.error(f"Failed to send email alert: {str(ex)}")

    @classmethod
    def _name(cls) -> str:
        return "email"

    @classmethod
    def _params(cls) -> List[BaseWebhookParameters]:
        return [
            BaseWebhookParameters('name', str, False, 'Webhook name'),
            BaseWebhookParameters('host', str, True, 'SMTP hostname or ip'),
            BaseWebhookParameters('port', int, False, 'SMTP Port', 587),
            BaseWebhookParameters('username', str, True, 'SMTP user'),
            BaseWebhookParameters('password', str, True, 'SMTP pass'),
            BaseWebhookParameters('from', str, True, 'SMTP from', attr_name='from_addr'),
            BaseWebhookParameters('to', list, True, 'SMTP to (string or list)', attr_name='to_addrs'),
            BaseWebhookParameters('use_tls', bool, False, 'Use SMTP_SSL', False),
            BaseWebhookParameters('subject', str, False, 'Email subject', '[ALERT] ClickDetect - {{rule.name}}'),
            BaseWebhookParameters('template', str, False, 'Email body template', DEFAULT_TEMPLATE),
        ]
