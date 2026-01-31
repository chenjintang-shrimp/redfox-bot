"""
基础用户卡片 minifilter
格式化基础统计数据
"""


def process(data: dict) -> dict:
    """
    基础格式化：PP、排名、游戏时间
    """
    statistics = data.get("statistics") or {}

    # PP 格式化
    pp = statistics.get("pp", 0)
    data["pp_formatted"] = f"{int(pp):,}"

    # 全球排名格式化
    global_rank = statistics.get("global_rank", 0)
    data["rank_formatted"] = f"#{int(global_rank):,}" if global_rank else "#-"

    # 国家排名格式化
    country_rank = statistics.get("country_rank", 0)
    data["country_rank_formatted"] = f"#{int(country_rank):,}" if country_rank else "#-"

    # 游戏时间格式化
    play_time = statistics.get("play_time", 0)
    hours = int(play_time // 3600)
    data["play_time_formatted"] = f"{hours:,}h"

    return data
