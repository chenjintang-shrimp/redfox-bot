from pathlib import Path

import yaml

from backend.expections import NoSkinAvailableError
from jinja2 import Environment, BaseLoader
from utils.logger import get_logger
from utils.variable import working_dir

logger = get_logger("renderer.skin")

_jinja_env = Environment(loader=BaseLoader())

SKINS_DIR = working_dir / "skins"

_skin_configs: dict[str, dict] = {}


def _load_skin_config(skin: str) -> dict | None:
    """
    加载皮肤的 skin.yaml 配置文件

    Args:
        skin: 皮肤名称

    Returns:
        配置字典，如果不存在则返回 None
    """
    if skin in _skin_configs:
        return _skin_configs[skin]

    skin_dir = SKINS_DIR / skin
    config_file = skin_dir / "skin.yaml"

    if not config_file.exists():
        _skin_configs[skin] = {}
        return None

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        _skin_configs[skin] = config
        logger.debug(f"已加载皮肤配置: {skin}")
        return config
    except Exception as e:
        logger.warning(f"加载皮肤配置失败: {skin}, {e}")
        _skin_configs[skin] = {}
        return None


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


def find_template(skin: str, renderer_name: str) -> Path | None:
    """
    查找模板文件，支持 skin.yaml 配置和 fallback 到 default

    优先级：
    1. 读取 skin.yaml 中的 templates 映射
    2. Fallback: 默认命名约定 {renderer_name}.html
    3. Fallback: default skin 的配置或默认模板

    Args:
        skin: 皮肤名称
        renderer_name: renderer 名称（如 "user_card", "user_beatmap_score_card"）

    Returns:
        模板文件路径，不存在则返回 None
    """
    skin_dir = SKINS_DIR / skin

    # 1. 尝试从 skin.yaml 配置中获取模板映射
    config = _load_skin_config(skin)
    if config and "templates" in config:
        template_filename = config["templates"].get(renderer_name)
        if template_filename:
            template_path = skin_dir / template_filename
            if template_path.exists():
                logger.debug(f"从配置找到模板: {renderer_name} -> {template_filename} (skin: {skin})")
                return template_path

    # 2. Fallback: 默认命名约定 {renderer_name}.html
    default_path = skin_dir / f"{renderer_name}.html"
    if default_path.exists():
        logger.debug(f"使用默认命名找到模板: {renderer_name}.html (skin: {skin})")
        return default_path

    # 3. Fallback: default skin
    if skin != "default":
        default_template = find_template("default", renderer_name)
        if default_template:
            logger.debug(f"模板 {renderer_name} 在 {skin} 中不存在，使用 default")
            return default_template

    # 4. 都不存在
    logger.warning(f"模板不存在: {renderer_name} (skin: {skin})")
    return None


async def render_template(skin: str, renderer_name: str, data: dict) -> str:
    """
    渲染模板

    Args:
        skin: 皮肤名称
        renderer_name: renderer 名称（如 "user_card", "user_beatmap_score_card"）
        data: 模板数据（已由调用方通过 minifilter 处理）

    Returns:
        渲染后的 HTML 字符串

    Raises:
        NoSkinAvailableError: 模板不存在（包括 fallback 到 default 也不存在）
    """
    template_path = find_template(skin, renderer_name)
    if template_path is None:
        raise NoSkinAvailableError(skin, renderer_name)

    template_str = template_path.read_text(encoding="utf-8")
    template = _jinja_env.from_string(template_str)

    return template.render(**data)
