"""
HTML 转图片渲染适配器

封装现有的 HTML → 图片渲染流程：
1. 应用 minifilters 处理数据
2. 使用 Jinja2 渲染 HTML 模板
3. 使用 html2image 转换为图片
"""

from typing import Any

from renderer.core import RenderAdapter, RenderResult
from renderer.skin_loader import find_template, render_template
from utils.flt_mgr import apply_minifilters_async
from utils.html2image import html_to_image
from utils.logger import get_logger
from utils.variable import DEFAULT_SKIN

logger = get_logger("renderer.adapters.html_image")


class HtmlImageAdapter(RenderAdapter):
    """
    HTML 转图片渲染适配器

    将数据通过 HTML 模板渲染，然后转换为 PNG 图片
    """

    async def render(
        self,
        view_name: str,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> RenderResult:
        """
        将数据渲染为图片

        Args:
            view_name: 视图名称，如 "user_card", "score_card"
            data: 渲染数据
            **kwargs: 额外参数
                - skin: 皮肤名称，默认使用 DEFAULT_SKIN
                - width: 图片宽度，默认 800
                - height: 图片高度，默认 400
                - locale: 语言代码

        Returns:
            RenderResult: content_type="image" 的渲染结果
        """
        skin = kwargs.get("skin") or self.config.get("default_skin", DEFAULT_SKIN)
        width = kwargs.get("width", 800)
        height = kwargs.get("height", 400)

        logger.info(f"[HtmlImageAdapter] 开始渲染 {view_name}, skin={skin}")

        # 1. 应用 minifilters 处理数据
        processed_data = await apply_minifilters_async(view_name, data)

        # 2. 渲染 HTML 模板
        html = await render_template(skin, view_name, processed_data)
        logger.debug(f"[HtmlImageAdapter] HTML 长度: {len(html)} chars")

        # 3. 转换为图片
        image_bytes = await html_to_image(html, width=width, height=height)
        logger.info(f"[HtmlImageAdapter] 图片生成完成，大小: {len(image_bytes)} bytes")

        return RenderResult(
            content_type="image",
            data=image_bytes,
            metadata={
                "format": "png",
                "width": width,
                "height": height,
                "engine": "html2image",
                "skin": skin,
                "view_name": view_name,
            },
        )

    def supports(self, view_name: str) -> bool:
        """
        检查是否支持渲染指定视图

        通过检查是否存在对应的 HTML 模板来判断

        Args:
            view_name: 视图名称

        Returns:
            bool: 是否存在对应的模板
        """
        # 检查 default skin 中是否存在模板
        template_path = find_template("default", view_name)
        return template_path is not None
