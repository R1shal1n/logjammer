"""Pluggable log sinks for Log Jammer OSS."""

from .base import BaseSink
from .file import FileSink
from .secops import SecOpsSink
from .syslog import SyslogSink
from .webhook import WebhookSink

__all__ = [
    "BaseSink",
    "FileSink",
    "SecOpsSink",
    "SyslogSink",
    "WebhookSink",
]
