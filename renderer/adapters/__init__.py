"""
渲染适配器模块

提供各种渲染引擎的适配器实现：
- HtmlImageAdapter: HTML 转图片渲染
- TextAdapter: 纯文本渲染
"""

from renderer.adapters.html_image import HtmlImageAdapter
from renderer.adapters.text import TextAdapter

__all__ = ["HtmlImageAdapter", "TextAdapter"]
