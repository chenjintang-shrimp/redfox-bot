import yaml
from utils.variable import STRINGS_FILE, API_FILE, working_dir
from utils.logger import get_logger

_STRINGS: dict = dict()


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


def format_template(name: str, **context) -> str:
    """
    name: 模板名称
    context: 模板变量
    """
    template = load_strings()[name]
    return template.format(**context)
