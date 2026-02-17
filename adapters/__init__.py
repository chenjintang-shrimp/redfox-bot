"""平台适配器包"""

from adapters.base import PlatformAdapter
from adapters.message_types import TextMessage, ImageMessage, EmbedMessage

__all__ = ["PlatformAdapter", "TextMessage", "ImageMessage", "EmbedMessage"]
