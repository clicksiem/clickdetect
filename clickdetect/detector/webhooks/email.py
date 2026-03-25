import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict, List
from logging import getLogger
from .base import BaseWebhook

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

    def to_dict(self) -> Dict:
        return {
            "type": EmailWebhook._name(),
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "from": self.from_addr,
            "to": self.to_addrs,
            "use_tls": self.use_tls,
            "subject": self.subject,
            "template": self.template,
        }

    async def _parse(self, data: Any):
        host = data.get("host")
        port = data.get("port", 587)
        username = data.get("username")
        password = data.get("password")
        from_addr = data.get("from")
        to_addrs = data.get("to")

        if not host or not username or not password or not from_addr or not to_addrs:
            raise Exception(
                "Invalid parameters: host, username, password, from and to are required"
            )

        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]

        self.name = data.get("name")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.use_tls = data.get("use_tls", False)
        self.subject = data.get("subject", "[ALERT] ClickDetect")
        self.template = data.get("template", DEFAULT_TEMPLATE)
