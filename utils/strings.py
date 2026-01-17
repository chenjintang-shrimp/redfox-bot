import json
from utils.variable import STRINGS_FILE, working_dir

_STRINGS: dict = dict()


def load_strings():
    global _STRINGS
    if not _STRINGS:
        path = working_dir / STRINGS_FILE
        with open(path, "r", encoding="utf-8") as f:
            _STRINGS = json.load(f)
    return _STRINGS


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
    """
    config = load_strings()[name]
    template = config["template"]
    context = {}
    if model is not None:
        fields = config.get("fields", [])
        for field_path in fields:
            key = field_path.split(".")[-1]
            value = get_nested_value(model, field_path)
            context[key] = value
    context.update(extra_context)
    return template.format(**context)
