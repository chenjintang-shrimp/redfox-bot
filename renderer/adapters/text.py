"""
纯文本渲染适配器

作为 fallback 方案，当图片渲染失败时使用
使用字符串模板生成纯文本消息
"""

from typing import Any

from renderer.core import RenderAdapter, RenderResult
from utils.logger import get_logger
from utils.strings import format_template

logger = get_logger("renderer.adapters.text")


class TextAdapter(RenderAdapter):
    """
    纯文本渲染适配器

    使用字符串模板生成纯文本消息，作为图片渲染失败的 fallback
    """

    async def render(
        self,
        view_name: str,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> RenderResult:
        """
        将数据渲染为纯文本

        Args:
            view_name: 视图名称
            data: 渲染数据
            **kwargs: 额外参数
                - locale: 语言代码，默认 "zh"

        Returns:
            RenderResult: content_type="text" 的渲染结果
        """
        locale = kwargs.get("locale", "zh")

        logger.info(f"[TextAdapter] 开始渲染 {view_name}")

        # 构建模板键名
        template_key = f"{view_name.upper()}_TEXT_TEMPLATE"

        try:
            # 尝试使用字符串模板
            text = format_template(template_key, locale=locale, **data)
        except Exception as e:
            # 如果模板不存在，使用简单的格式化
            logger.warning(f"[TextAdapter] 模板 {template_key} 不存在: {e}")
            text = self._fallback_format(view_name, data)

        logger.info(f"[TextAdapter] 文本渲染完成，长度: {len(text)} chars")

        return RenderResult(
            content_type="text",
            data=text,
            metadata={
                "engine": "text",
                "view_name": view_name,
                "locale": locale,
            },
        )

    def supports(self, view_name: str) -> bool:
        """
        检查是否支持渲染指定视图

        文本适配器总是支持，作为最终的 fallback

        Args:
            view_name: 视图名称

        Returns:
            bool: 总是返回 True
        """
        return True

    def _fallback_format(self, view_name: str, data: dict[str, Any]) -> str:
        """
        Fallback 格式化方法

        当字符串模板不存在时，使用简单的键值对格式

        Args:
            view_name: 视图名称
            data: 渲染数据

        Returns:
            str: 格式化的文本
        """
        lines = [f"【{view_name}】"]

        # 提取关键字段
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, dict) and "username" in value:
                lines.append(f"{key}: {value['username']}")

        return "\n".join(lines)
