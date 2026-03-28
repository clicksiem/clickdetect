from attr import dataclass
from datetime import datetime, timedelta, timezone
from re import fullmatch
from typing import Any, Type
from datetime import date
from uuid import UUID
from dataclasses import is_dataclass, asdict
import socket
import uuid

UNITS_IN_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 24 * 60 * 60,
    "w": 7 * 24 * 60 * 60,
    "mo": 30 * 24 * 60 * 60,
    "y": 365 * 24 * 60 * 60,
}


def machine_device_id() -> str:
    machine_key = f"{socket.gethostname()}-{uuid.getnode()}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, machine_key))


def parse_interval_to_time(interval: str):
    pattern = r"([\d.]+)\s*(s|m|h|d|w|mo|y)"
    match = fullmatch(pattern, interval.strip())
    if not match:
        raise ValueError(
            f"Invalid interval unit format {interval}. Try: 1m, 30s, 1y, etc..."
        )
    value, unit = match.groups()
    seconds = float(value) * UNITS_IN_SECONDS[unit]
    end = datetime.now(timezone.utc)
    start = end - timedelta(seconds=seconds)
    return start, end


def parse_interval_to_ns(interval: str):
    start, end = parse_interval_to_time(interval)
    end_ns = int(end.timestamp() * 1e9)
    start_ns = int(start.timestamp() * 1e9)
    return start_ns, end_ns


def parse_interval_to_seconds(interval: str):
    pattern = r"([\d.]+)\s*(s|m|h|d|w|mo|y)"
    match = fullmatch(pattern, interval.strip())
    if not match:
        raise ValueError(
            f"Invalid interval format {interval}. Try: 1m, 30s, 1h, etc..."
        )
    value, unit = match.groups()
    seconds = float(value) * UNITS_IN_SECONDS[unit]
    return seconds


def json_serializer(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


@dataclass
class Parameters:
    name: str
    type: Type
    required: bool
    help: str = ''
    default: Any | None = None
    attr_name: str | None = None  # attribute name when it differs from the config key
