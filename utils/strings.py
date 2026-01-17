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


def format_template(name: str, model=None, **kwargs) -> str:
    """格式化模板"""
    config = load_strings()[name]
    template = config["template"]

    # 从模型提取字段值
    if model is not None:
        for field in config.get("fields", []):
            key = field.split(".")[-1]  # statistics.pp -> pp
            if key not in kwargs:
                kwargs[key] = get_nested_value(model, field)

    return template.format(**kwargs)
