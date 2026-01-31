from pathlib import Path

from backend.expections import NoSkinAvailableError
from jinja2 import Environment, BaseLoader
from utils.flt_mgr import apply_minifilters_async
from utils.logger import get_logger
from utils.variable import working_dir

logger = get_logger("renderer.skin")

_jinja_env = Environment(loader=BaseLoader())

SKINS_DIR = working_dir / "skins"


def _scan_skin_templates(skin: str) -> dict[str, Path]:
    """扫描指定皮肤的所有模板文件"""
    skin_dir = SKINS_DIR / skin
    if not skin_dir.exists():
        return {}

    templates = {}
    for html_file in skin_dir.glob("*.html"):
        template_name = html_file.stem
        templates[template_name] = html_file

    return templates


def find_template(skin: str, template_name: str) -> Path | None:
    """
    查找模板文件，支持 fallback 到 default

    1. 先查找指定 skin
    2. 不存在则 fallback 到 default
    3. 都不存在返回 None
    """
    # 1. 查找指定 skin
    skin_templates = _scan_skin_templates(skin)
    if template_name in skin_templates:
        return skin_templates[template_name]

    # 2. fallback 到 default
    if skin != "default":
        default_templates = _scan_skin_templates("default")
        if template_name in default_templates:
            logger.debug(f"模板 {template_name} 在 {skin} 中不存在，使用 default")
            return default_templates[template_name]

    # 3. 都不存在
    logger.warning(f"模板不存在: {template_name} (skin: {skin})")
    return None


async def render_template(skin: str, template_name: str, data: dict) -> str:
    """
    渲染模板

    Args:
        skin: 皮肤名称
        template_name: 模板名称
        data: 模板数据

    Returns:
        渲染后的 HTML 字符串

    Raises:
        NoSkinAvailableError: 模板不存在（包括 fallback 到 default 也不存在）
    """
    template_path = find_template(skin, template_name)
    if template_path is None:
        raise NoSkinAvailableError(skin, template_name)

    # 应用 minifilters 处理数据（异步版本）
    processed_data = await apply_minifilters_async(template_name, data)

    template_str = template_path.read_text(encoding="utf-8")
    template = _jinja_env.from_string(template_str)

    return template.render(**processed_data)
