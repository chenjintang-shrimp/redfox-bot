    # Minifilter 开发指南

    ## 什么是 Minifilter？

    Minifilter 是一个数据加工系统，用于在渲染前对 API 返回的数据进行处理。你可以：

    - 格式化数值（如 PP、排名等）
    - 添加计算字段
    - 转换数据格式
    - 添加自定义字段

    ## 目录结构

    每个 minifilter 是一个独立的包，放在 `minifilters/` 目录下：

    ```
    minifilters/
    └── your_minifilter/          # minifilter 目录名
        ├── __init__.py           # 必须包含 process() 函数
        └── minifilter.yaml       # 配置文件
    ```

    ## 配置文件 (minifilter.yaml)

    ```yaml
    name: your_minifilter        # minifilter 名称（唯一）
    version: 1.0.0              # 版本号
    description: "描述信息"     # 描述

    hooks:                      # 要 hook 的 renderer 列表
    - user_card
    - score_card

    depends:                    # 依赖的其他 minifilter（按顺序执行）
    - other_minifilter
    ```

    ## 实现文件 (__init__.py)

    必须定义 `process(data: dict) -> dict` 函数：

    ```python
    def process(data: dict) -> dict:
        """
        处理数据
        
        Args:
            data: 原始 API 数据（可能已被其他 minifilter 处理过）
        
        Returns:
            处理后的数据
        """
        # 读取原始字段
        statistics = data.get("statistics") or {}
        
        # 添加格式化字段
        pp = statistics.get("pp", 0)
        data["pp_formatted"] = f"{int(pp):,}"
        
        # 返回处理后的数据
        return data
    ```

    ## 完整示例

    ### 基础用户卡片格式化 (user_card_basic)

    ```python
    # minifilters/user_card_basic/__init__.py

    def process(data: dict) -> dict:
        """基础用户卡片格式化"""
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
        
        # 游戏时间格式化（转换为小时）
        play_time = statistics.get("play_time", 0)
        hours = int(play_time // 3600)
        data["play_time_formatted"] = f"{hours:,}h"
        
        return data
    ```

    ```yaml
    # minifilters/user_card_basic/minifilter.yaml
    name: user_card_basic
    version: 1.0.0
    description: 基础用户卡片格式化

    hooks:
    - user_card

    depends: []
    ```

    ### 依赖其他 minifilter

    ```python
    # minifilters/user_card_extra/__init__.py

    def process(data: dict) -> dict:
        """额外用户卡片格式化（在 basic 之后执行）"""
        statistics = data.get("statistics") or {}
        
        # 准确率格式化
        accuracy = statistics.get("hit_accuracy", 0)
        data["accuracy_formatted"] = f"{accuracy:.2f}%"
        
        # 最高连击
        max_combo = statistics.get("maximum_combo", 0)
        data["max_combo_formatted"] = f"{int(max_combo):,}"
        
        return data
    ```

    ```yaml
    # minifilters/user_card_extra/minifilter.yaml
    name: user_card_extra
    version: 1.0.0
    description: 额外用户卡片格式化

    hooks:
    - user_card

    depends:
    - user_card_basic    # 确保在 basic 之后执行
    ```

    ## 可用数据字段

    所有字段定义来自 **osu! API v2** (osu-web)。以下是常用字段：

    ### 用户数据 (User)

    | 字段 | 类型 | 说明 | 示例 |
    |------|------|------|------|
    | `id` | int | 用户 ID | 12345678 |
    | `username` | str | 用户名 | "peppy" |
    | `avatar_url` | str | 头像 URL | "https://..." |
    | `country` | object | 国家信息 | `{"code": "JP", "name": "Japan"}` |
    | `country.code` | str | 国家代码 | "JP" |
    | `country.name` | str | 国家名称 | "Japan" |
    | `statistics` | object | 统计数据 | 见下表 |

    ### 统计数据 (UserStatistics)

    | 字段 | 类型 | 说明 |
    |------|------|------|
    | `pp` | float | Performance Points |
    | `global_rank` | int | 全球排名 |
    | `country_rank` | int | 国家排名 |
    | `hit_accuracy` | float | 准确率 (%) |
    | `play_count` | int | 游戏次数 |
    | `play_time` | int | 游戏时间 (秒) |
    | `maximum_combo` | int | 最高连击 |
    | `total_hits` | int | 总命中次数 |
    | `ranked_score` | int | Ranked 谱面总分 |
    | `total_score` | int | 总分 |

    ### 谱面数据 (Beatmap)

    | 字段 | 类型 | 说明 |
    |------|------|------|
    | `id` | int | 谱面 ID |
    | `beatmapset_id` | int | 谱面集 ID |
    | `version` | str | 难度名 |
    | `difficulty_rating` | float | 难度星级 |
    | `mode` | str | 游戏模式 (osu/taiko/catch/mania) |
    | `total_length` | int | 总时长 (秒) |
    | `hit_length` | int | 游玩时长 (秒) |
    | `bpm` | float | BPM |
    | `cs` | float | Circle Size |
    | `drain` | float | HP Drain |
    | `accuracy` | float | Overall Difficulty |
    | `ar` | float | Approach Rate |

    ### 成绩数据 (Score)

    | 字段 | 类型 | 说明 |
    |------|------|------|
    | `id` | int | 成绩 ID |
    | `user_id` | int | 用户 ID |
    | `accuracy` | float | 准确率 |
    | `mods` | list | 使用的 Mods |
    | `score` | int | 分数 |
    | `max_combo` | int | 最大连击 |
    | `passed` | bool | 是否通过 |
    | `pp` | float | PP 值 |
    | `rank` | str | 成绩等级 (SS/S/A/B/C/D) |
    | `created_at` | str | 成绩时间 |
    | `statistics` | object | 详细统计 |

    ## 依赖系统

    ### 执行顺序

    FltMgr 使用拓扑排序自动计算执行顺序：

    ```
    A (无依赖) → B (依赖 A) → C (依赖 B)
    ```

    ### 循环依赖

    如果存在循环依赖（A 依赖 B，B 依赖 A），该 hook 的所有 minifilter 将被禁用。

    ## 最佳实践

    1. **单一职责**：每个 minifilter 只做一件事
    2. **命名规范**：使用 `hook_name_功能` 格式命名
    3. **防御编程**：使用 `.get()` 避免 KeyError
    4. **添加新字段**：不要修改原始字段，添加新的格式化字段
    5. **文档注释**：在 `__init__.py` 中添加文档字符串

    ## 调试技巧

    查看日志确认 minifilter 加载情况：

    ```
    [FltMgr] 已加载: user_card_basic (hooks: ['user_card'], depends: [])
    [FltMgr] 执行链 [user_card]: user_card_basic -> user_card_extra
    [FltMgr] 已编译 [user_card]: 2 个处理器
    ```

    ## 参考文档

    - [osu! API v2 文档](https://osu.ppy.sh/docs/index.html)
    - 本项目的 `minifilters/user_card_basic/` 和 `minifilters/user_card_extra/` 作为参考实现
