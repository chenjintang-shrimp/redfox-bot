"""
额外用户卡片 minifilter
添加更多格式化字段
"""


def process(data: dict) -> dict:
    """
    额外格式化：准确率、连击等
    """
    statistics = data.get("statistics") or {}

    # 准确率格式化
    accuracy = statistics.get("hit_accuracy", 0)
    data["accuracy_formatted"] = f"{accuracy:.2f}%"

    # 最高连击
    max_combo = statistics.get("maximum_combo", 0)
    data["max_combo_formatted"] = f"{int(max_combo):,}"

    # 总游戏次数
    play_count = statistics.get("play_count", 0)
    data["play_count_formatted"] = f"{int(play_count):,}"

    return data
