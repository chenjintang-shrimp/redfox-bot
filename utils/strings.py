import yaml
from jinja2 import Environment, BaseLoader
from utils.variable import STRINGS_FILE, API_FILE, working_dir
from utils.logger import get_logger

_STRINGS: dict = dict()

# 创建 Jinja2 环境
_jinja_env = Environment(loader=BaseLoader())


def load_strings():
    global _STRINGS
    if not _STRINGS:
        path = working_dir / STRINGS_FILE
        with open(path, "r", encoding="utf-8") as f:
            _STRINGS = yaml.safe_load(f)
        get_logger("utils").info(f"Loaded strings from YAML: {path}")
    return _STRINGS


# 加载 API 配置
API_DICT = yaml.safe_load(open(working_dir / API_FILE, "r", encoding="utf-8"))


def get_api_url(endpoint: str, **kwargs) -> str:
    """根据端点名称获取完整的 API URL"""
    api_config = API_DICT["apis"]
    base_url = API_DICT["api_prefix"]
    return f"{base_url}{api_config[endpoint]}".format(**kwargs)


def format_template(name: str, context: dict | None = None, **kwargs) -> str:
    """
    使用 Jinja2 渲染模板

    Args:
        name: 模板名称
        context: 模板变量字典（可选）
        kwargs: 额外的模板变量

    Returns:
        渲染后的字符串
    """
    template_str = load_strings()[name]

    # 合并字典参数和关键字参数
    merged_context = {}
    if context:
        merged_context.update(context)
    merged_context.update(kwargs)

    # 使用 Jinja2 渲染模板
    template = _jinja_env.from_string(template_str)
    return template.render(**merged_context)
