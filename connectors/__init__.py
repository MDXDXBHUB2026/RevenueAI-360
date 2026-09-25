"""Connectors package initialization."""
from connectors.base import ChannelConnector, DispatchResult
from connectors.demo_connector import (
    DemoChannelConnector,
    EmailConnector,
    WhatsAppConnector,
    SlackConnector,
)

__all__ = [
    "ChannelConnector",
    "DispatchResult",
    "DemoChannelConnector",
    "EmailConnector",
    "WhatsAppConnector",
    "SlackConnector",
]
