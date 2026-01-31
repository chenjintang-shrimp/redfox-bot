import importlib

import pkgutil
from typing import Callable, Dict
from utils.logger import get_logger


logger = get_logger("minifilters")


_minifilters: Dict[str, Callable[[dict], dict]] = {}


def minifilter(template_name: str):
    """


    装饰器：注册 minifilter



    用法:


        @register("user_card")


        def process(data: dict) -> dict:


            data['pp_formatted'] = f"{data.get('pp', 0):,}"
            return data
    """

    def decorator(func: Callable[[dict], dict]) -> Callable[[dict], dict]:
        _minifilters[template_name] = func

        logger.info(
            f"[minifilter] 已注册: {template_name} -> {func.__module__}.{func.__name__}"
        )
        return func

    return decorator


def get_minifilter(template_name: str) -> Callable[[dict], dict] | None:
    """获取指定 minifilter"""

    return _minifilters.get(template_name)


def apply_minifilter(template_name: str, data: dict) -> dict:
    """


    应用 minifilter 加工数据



    如果 minifilter 不存在，返回原始数据
    """

    minifilter = get_minifilter(template_name)

    if minifilter is None:
        logger.warning(f"[minifilter] 未找到: {template_name}，使用原始数据")

        logger.debug(f"[minifilter] 当前已注册: {list(_minifilters.keys())}")
        return data

    try:
        logger.info(f"[minifilter] 开始执行: {template_name}")

        logger.debug(f"[minifilter] 输入数据 keys: {list(data.keys())}")

        result = minifilter(data.copy())

        logger.info(f"[minifilter] 执行完成: {template_name}")

        logger.debug(
            f"[minifilter] 输出数据新增 keys: {list(set(result.keys()) - set(data.keys()))}"
        )
        return result

    except Exception as e:
        logger.error(f"[minifilter] {template_name} 执行失败: {e}", exc_info=True)
        return data


def auto_discover_minifilters(package_name: str = "minifilters") -> None:
    """

    自动扫描 minifilters 包及其子包

    导入所有模块以触发装饰器注册
    """

    try:
        package = importlib.import_module(package_name)

    except ImportError as e:
        logger.warning(f"无法导入包 {package_name}: {e}")
        return

    if not hasattr(package, "__path__"):
        return

    count = 0

    for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
        full_name = f"{package_name}.{name}"

        try:
            importlib.import_module(full_name)

            count += 1

            if is_pkg:
                auto_discover_minifilters(full_name)

        except Exception as e:
            logger.warning(f"导入 minifilter 模块 {full_name} 失败: {e}")

    logger.info(
        f"[minifilter] 扫描完成，共导入 {count} 个模块，注册了 {len(_minifilters)} 个处理器"
    )

    logger.info(f"[minifilter] 已注册列表: {list(_minifilters.keys())}")


def get_all_minifilters() -> Dict[str, Callable[[dict], dict]]:
    """获取所有已注册的 minifilter"""

    return _minifilters.copy()
