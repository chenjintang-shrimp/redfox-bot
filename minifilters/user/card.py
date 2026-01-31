from minifilters import minifilter



@minifilter("user_card")

def process(data: dict) -> dict:
    """

    用户卡片数据加工


    添加格式化字段和计算字段
    """

    statistics = data.get("statistics") or {}


    pp = statistics.get("pp", 0)

    data["pp_formatted"] = f"{pp:,}"


    global_rank = statistics.get("global_rank", 0)

    data["rank_formatted"] = f"#{global_rank:,}" if global_rank else "#-"


    country_rank = statistics.get("country_rank", 0)

    data["country_rank_formatted"] = f"#{country_rank:,}" if country_rank else "#-"


    play_time = statistics.get("play_time", 0)

    data["play_time_hours"] = play_time // 3600


    if pp >= 10000:
        data["tier"] = "diamond"

        data["tier_color"] = "#b9f2ff"

    elif pp >= 7000:

        data["tier"] = "platinum"

        data["tier_color"] = "#e5e4e2"

    elif pp >= 4000:

        data["tier"] = "gold"

        data["tier_color"] = "#ffd700"

    elif pp >= 2000:

        data["tier"] = "silver"

        data["tier_color"] = "#c0c0c0"

    else:

        data["tier"] = "bronze"

        data["tier_color"] = "#cd7f32"


    return data

