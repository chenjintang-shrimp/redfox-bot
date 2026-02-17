"""统一的消息类型定义

用于在各层之间传递消息，与具体平台无关
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class TextMessage:
    """文本消息"""

    content: str

    def __str__(self) -> str:
        return self.content


@dataclass
class ImageMessage:
    """图片消息

    Attributes:
        image_bytes: 图片字节数据
        filename: 文件名（可选）
        caption: 图片说明文字（可选）
    """

    image_bytes: bytes
    filename: Optional[str] = None
    caption: Optional[str] = None


@dataclass
class EmbedMessage:
    """富文本/嵌入消息（主要用于 Discord）

    QQ 平台可以将其转换为文字+图片形式
    """

    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[int] = None
    fields: Optional[list[dict[str, Any]]] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    footer: Optional[str] = None


# 联合类型，表示任何类型的消息
Message = TextMessage | ImageMessage | EmbedMessage
