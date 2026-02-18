"""
统一渲染服务

提供渲染引擎的管理和路由功能：
1. 注册多个渲染引擎
2. 自动选择最佳引擎
3. 支持自动 fallback（图片失败时 fallback 到文本）
4. 确保总有 RenderResult 返回
"""

from typing import Any

from renderer.core import RenderEngine, RenderResult
from utils.logger import get_logger

logger = get_logger("renderer.service")


class RenderService:
    """
    统一渲染服务

    管理和路由到不同的渲染引擎，支持自动 fallback
    """

    def __init__(self) -> None:
        """初始化渲染服务"""
        self._engines: list[RenderEngine] = []
        self._default_engine: RenderEngine | None = None

    def register_engine(
        self,
        engine: RenderEngine,
        default: bool = False,
    ) -> None:
        """
        注册渲染引擎

        Args:
            engine: 渲染引擎实例
            default: 是否设为默认引擎
        """
        self._engines.append(engine)
        if default or self._default_engine is None:
            self._default_engine = engine
            logger.info(f"[RenderService] 已注册默认引擎: {type(engine).__name__}")
        else:
            logger.info(f"[RenderService] 已注册引擎: {type(engine).__name__}")

    async def render(
        self,
        view_name: str,
        data: dict[str, Any],
        preferred_engine: str | None = None,
        **kwargs: Any,
    ) -> RenderResult:
        """
        渲染数据为 RenderResult

        渲染流程：
        1. 尝试 preferred_engine（如果指定）
        2. 尝试 default_engine
        3. 尝试其他支持的引擎
        4. 如果图片渲染失败，自动 fallback 到文本渲染

        Args:
            view_name: 视图名称
            data: 渲染数据
            preferred_engine: 优先使用的引擎类型（"html_image", "text"）
            **kwargs: 额外参数传递给渲染引擎

        Returns:
            RenderResult: 渲染结果（保证返回，不会抛出异常）
        """
        logger.info(f"[RenderService] 开始渲染 {view_name}")

        # 1. 尝试优先引擎（如果指定）
        if preferred_engine:
            for engine in self._engines:
                if self._get_engine_name(engine) == preferred_engine:
                    try:
                        if engine.supports(view_name):
                            result = await engine.render(view_name, data, **kwargs)
                            logger.info(
                                f"[RenderService] 使用 {preferred_engine} 渲染成功"
                            )
                            return result
                    except Exception as e:
                        logger.warning(
                            f"[RenderService] {preferred_engine} 渲染失败: {e}"
                        )

        # 2. 尝试默认引擎
        if self._default_engine and self._default_engine.supports(view_name):
            try:
                result = await self._default_engine.render(view_name, data, **kwargs)
                logger.info("[RenderService] 使用默认引擎渲染成功")
                return result
            except Exception as e:
                logger.warning(f"[RenderService] 默认引擎渲染失败: {e}")

        # 3. 尝试其他支持的引擎
        for engine in self._engines:
            if engine == self._default_engine:
                continue  # 跳过已尝试的默认引擎
            try:
                if engine.supports(view_name):
                    result = await engine.render(view_name, data, **kwargs)
                    logger.info(
                        f"[RenderService] 使用 {type(engine).__name__} 渲染成功"
                    )
                    return result
            except Exception as e:
                logger.warning(f"[RenderService] {type(engine).__name__} 渲染失败: {e}")

        # 4. 所有引擎都失败，尝试文本 fallback
        logger.error("[RenderService] 所有引擎渲染失败，尝试文本 fallback")
        for engine in self._engines:
            if self._get_engine_name(engine) == "text":
                try:
                    result = await engine.render(view_name, data, **kwargs)
                    logger.info("[RenderService] 文本 fallback 成功")
                    return result
                except Exception as e:
                    logger.error(f"[RenderService] 文本 fallback 也失败: {e}")

        # 5. 真的没有任何办法了，返回一个错误消息
        logger.critical(f"[RenderService] 完全无法渲染 {view_name}")
        return RenderResult(
            content_type="text",
            data=f"渲染失败: 无法渲染视图 {view_name}",
            metadata={"error": True, "view_name": view_name},
        )

    def _get_engine_name(self, engine: RenderEngine) -> str:
        """
        获取引擎的名称标识

        Args:
            engine: 渲染引擎

        Returns:
            str: 引擎名称（小写类名去掉 Adapter 后缀）
        """
        class_name = type(engine).__name__.lower()
        return class_name.replace("adapter", "")


# 全局渲染服务实例
render_service = RenderService()


def init_render_service() -> RenderService:
    """
    初始化渲染服务

    注册默认的渲染引擎：
    - HtmlImageAdapter: 默认引擎，用于图片渲染
    - TextAdapter: fallback 引擎，用于文本渲染

    Returns:
        RenderService: 初始化完成的渲染服务
    """
    from renderer.adapters.html_image import HtmlImageAdapter
    from renderer.adapters.text import TextAdapter

    # 注册 HTML 图片引擎（默认）
    html_adapter = HtmlImageAdapter()
    render_service.register_engine(html_adapter, default=True)

    # 注册文本引擎（fallback）
    text_adapter = TextAdapter()
    render_service.register_engine(text_adapter)

    logger.info("[RenderService] 初始化完成")
    return render_service
