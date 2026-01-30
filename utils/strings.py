import json
from pathlib import Path
from utils.variable import STRINGS_FILE, API_FILE, working_dir
from utils.logger import get_logger

_STRINGS: dict = dict()


def load_strings():
    global _STRINGS
    if not _STRINGS:
        path = working_dir / STRINGS_FILE
        
        # 根据文件扩展名选择解析方式
        if path.suffix.lower() in ('.yaml', '.yml'):
            try:
                import yaml
                with open(path, "r", encoding="utf-8") as f:
                    _STRINGS = yaml.safe_load(f)
                get_logger("utils").info(f"Loaded strings from YAML: {path}")
            except ImportError:
                get_logger("utils").error("PyYAML not installed, cannot load YAML strings file")
                raise
        else:
            # 默认使用 JSON
            with open(path, "r", encoding="utf-8") as f:
                _STRINGS = json.load(f)
            get_logger("utils").info(f"Loaded strings from JSON: {path}")
            
    return _STRINGS


# 加载 API 配置（优先 YAML，其次 JSON）
api_path = working_dir / API_FILE
if api_path.suffix.lower() in ('.yaml', '.yml'):
    import yaml
    API_DICT = yaml.safe_load(open(api_path, "r", encoding="utf-8"))
else:
    API_DICT = json.load(open(api_path, "r", encoding="utf-8"))


def get_api_url(endpoint: str, **kwargs) -> str:
    """根据端点名称获取完整的 API URL"""
    api_config = API_DICT["apis"]
    base_url = API_DICT["api_prefix"]
    return f"{base_url}{api_config[endpoint]}".format(**kwargs)


def get_nested_value(obj, path: str):
    """从嵌套的 Pydantic 模型或字典中获取值"""
    value = obj
    for key in path.split("."):
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = getattr(value, key, None)
    return value


def format_template(name: str, model=None, **extra_context) -> str:
    """
    name: 模板名称
    model: 主要数据源 (Pydantic对象 / 字典 / 数据库对象)
    extra_context: 额外的上下文变量 (比如 error_msg="未找到用户")
    
    支持两种格式:
    1. 简化格式: "TEMPLATE_NAME": "template string"
    2. 完整格式: "TEMPLATE_NAME": {"template": "...", "fields": [...]}
    """
    config = load_strings()[name]
    
    # 简化格式：直接是字符串
    if isinstance(config, str):
        template = config
        context = extra_context
    # 完整格式：包含 template 和 fields
    elif isinstance(config, dict):
        template = config["template"]
        context = {}
        if model is not None:
            fields = config.get("fields", [])
            for field_path in fields:
                key = field_path.split(".")[-1]
                value = get_nested_value(model, field_path)
                context[key] = value
        context.update(extra_context)
    else:
        raise ValueError(f"Invalid template format for {name}: {type(config)}")
    
    return template.format(**context)
