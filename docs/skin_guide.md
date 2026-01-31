# Skin 编撰指南

## 概述

Skin 是基于 HTML/CSS 的模板系统，使用 Jinja2 作为模板引擎。本指南将帮助你创建美观、高效的皮肤。

## 目录结构

```
skins/
└── your_skin/                # 皮肤目录名
    ├── user_card.html        # 用户卡片模板
    ├── score_card.html       # 成绩卡片模板
    └── style.css             # (可选) 样式文件
```

## 基本原则

### 1. 优先使用官方 API 字段

**推荐做法：**
```html
<!-- 直接使用 API 原始字段 -->
<div class="username">{{ username }}</div>
<div class="country">{{ country.name }}</div>
<div class="pp">{{ statistics.pp }}</div>
```

**不推荐做法：**
```html
<!-- 不要为了自定义字段名而创建 minifilter -->
<div class="pp">{{ pp_formatted }}</div>  <!-- 需要 minifilter 转换 -->
```

**例外情况：** 只有当需要复杂计算或格式化时才使用 minifilter。

### 2. 充分利用 Jinja2 特性

#### 过滤器 (Filters)

```html
<!-- 数值格式化 -->
<div class="pp">{{ statistics.pp | int }}</div>
<div class="accuracy">{{ statistics.hit_accuracy | round(2) }}%</div>

<!-- 字符串处理 -->
<div class="username">{{ username | upper }}</div>
<div class="title">{{ beatmap.title | truncate(30) }}</div>

<!-- 默认值 -->
<div class="rank">#{{ statistics.global_rank | default('N/A') }}</div>

<!-- 列表操作 -->
<div class="mods">{{ mods | join(', ') }}</div>
```

#### 条件语句

```html
{% if statistics.global_rank %}
    <div class="rank">#{{ statistics.global_rank }}</div>
{% else %}
    <div class="rank">无排名</div>
{% endif %}

<!-- 简写形式 -->
<div class="rank">{{ '#' ~ statistics.global_rank if statistics.global_rank else '无排名' }}</div>
```

#### 循环

```html
<!-- 遍历成绩列表 -->
{% for score in scores %}
    <div class="score-item">
        <span>{{ score.rank }}</span>
        <span>{{ score.pp | round(2) }}pp</span>
    </div>
{% endfor %}

<!-- 带索引 -->
{% for score in scores %}
    <div class="score-item">
        <span>#{{ loop.index }}</span>
        <span>{{ score.rank }}</span>
    </div>
{% endfor %}
```

#### 宏 (Macros)

```html
<!-- 定义宏 -->
{% macro render_stat(label, value, unit='') %}
    <div class="stat">
        <div class="stat-value">{{ value }}{{ unit }}</div>
        <div class="stat-label">{{ label }}</div>
    </div>
{% endmacro %}

<!-- 使用宏 -->
{{ render_stat('PP', statistics.pp | int) }}
{{ render_stat('Accuracy', statistics.hit_accuracy | round(2), '%') }}
```

### 3. 内联样式 vs 外部样式

**推荐：内联样式**
```html
<style>
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
    }
</style>
<div class="card">
    <!-- 内容 -->
</div>
```

**原因：**
- 单个文件即可完成皮肤
- 便于分享和安装
- 渲染时不需要额外请求 CSS 文件

### 4. 响应式设计

```html
<style>
    .card {
        width: 800px;
        height: 400px;
        /* 固定尺寸确保截图一致 */
    }
    
    .stats {
        display: flex;
        justify-content: space-around;
    }
    
    .stat {
        text-align: center;
        flex: 1;
    }
</style>
```

## 可用数据字段

所有字段来自 **osu! API v2** (osu-web)。

### 用户卡片 (user_card)

```html
<!-- 基础信息 -->
{{ id }}                    <!-- 用户 ID -->
{{ username }}              <!-- 用户名 -->
{{ avatar_url }}            <!-- 头像 URL -->
{{ cover_url }}             <!-- 封面 URL -->
{{ join_date }}             <!-- 注册时间 -->

<!-- 国家信息 -->
{{ country.code }}          <!-- 国家代码 (如 "JP") -->
{{ country.name }}          <!-- 国家名称 (如 "Japan") -->

<!-- 游戏模式 -->
{{ playmode }}              <!-- 当前模式 (osu/taiko/catch/mania) -->

<!-- 统计数据 (statistics) -->
{{ statistics.pp }}                     <!-- PP -->
{{ statistics.global_rank }}            <!-- 全球排名 -->
{{ statistics.country_rank }}           <!-- 国家排名 -->
{{ statistics.hit_accuracy }}           <!-- 准确率 -->
{{ statistics.play_count }}             <!-- 游戏次数 -->
{{ statistics.play_time }}              <!-- 游戏时间 (秒) -->
{{ statistics.maximum_combo }}          <!-- 最高连击 -->
{{ statistics.total_hits }}             <!-- 总命中次数 -->
{{ statistics.ranked_score }}           <!-- Ranked 总分 -->
{{ statistics.total_score }}            <!-- 总分 -->

<!-- 等级信息 -->
{{ statistics.level.current }}          <!-- 当前等级 -->
{{ statistics.level.progress }}         <!-- 等级进度 (0-100) -->

<!-- 成绩统计 -->
{{ statistics.grade_counts.ss }}        <!-- SS 数量 -->
{{ statistics.grade_counts.ssh }}       <!-- SSH 数量 -->
{{ statistics.grade_counts.s }}         <!-- S 数量 -->
{{ statistics.grade_counts.sh }}        <!-- SH 数量 -->
{{ statistics.grade_counts.a }}         <!-- A 数量 -->
```

### 成绩卡片 (score_card)

```html
<!-- 基础信息 -->
{{ id }}                    <!-- 成绩 ID -->
{{ user_id }}               <!-- 用户 ID -->
{{ accuracy }}              <!-- 准确率 -->
{{ mods }}                  <!-- Mods 列表 -->
{{ score }}                 <!-- 分数 -->
{{ max_combo }}             <!-- 最大连击 -->
{{ passed }}                <!-- 是否通过 -->
{{ pp }}                    <!-- PP -->
{{ rank }}                  <!-- 成绩等级 (XH/X/SH/S/A/B/C/D) -->
{{ created_at }}            <!-- 成绩时间 -->

<!-- 谱面信息 (beatmap) -->
{{ beatmap.id }}
{{ beatmap.beatmapset_id }}
{{ beatmap.version }}       <!-- 难度名 -->
{{ beatmap.difficulty_rating }}  <!-- 星级 -->
{{ beatmap.mode }}
{{ beatmap.total_length }}
{{ beatmap.hit_length }}
{{ beatmap.bpm }}
{{ beatmap.cs }}
{{ beatmap.drain }}
{{ beatmap.accuracy }}      <!-- OD -->
{{ beatmap.ar }}

<!-- 谱面集信息 (beatmapset) -->
{{ beatmapset.title }}
{{ beatmapset.artist }}
{{ beatmapset.creator }}    <!-- 作者用户名 -->
{{ beatmapset.status }}     <!-- ranked/approved/loved 等 -->

<!-- 统计信息 (statistics) -->
{{ statistics.count_300 }}
{{ statistics.count_100 }}
{{ statistics.count_50 }}
{{ statistics.count_miss }}
{{ statistics.count_geki }}     <!-- Mania Perfect -->
{{ statistics.count_katu }}     <!-- Mania Good -->
```

## 完整示例

### 简约用户卡片

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 800px;
            height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            width: 700px;
            display: flex;
            gap: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .avatar {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 4px solid #667eea;
        }
        
        .info {
            flex: 1;
        }
        
        .username {
            font-size: 36px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .country {
            font-size: 18px;
            color: #666;
            margin-bottom: 20px;
        }
        
        .stats {
            display: flex;
            gap: 30px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 14px;
            color: #999;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="card">
        <img class="avatar" src="{{ avatar_url }}" alt="avatar">
        <div class="info">
            <div class="username">{{ username }}</div>
            <div class="country">{{ country.name }} ({{ country.code }})</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{{ statistics.pp | int }}</div>
                    <div class="stat-label">PP</div>
                </div>
                <div class="stat">
                    <div class="stat-value">#{{ statistics.global_rank | default('-') }}</div>
                    <div class="stat-label">Global Rank</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ statistics.hit_accuracy | round(2) }}%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{{ (statistics.play_time / 3600) | int }}h</div>
                    <div class="stat-label">Play Time</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

## 调试技巧

1. **查看可用字段**：在模板中添加 `{{ data | tojson }}` 查看所有数据
2. **检查渲染结果**：使用浏览器的开发者工具检查 HTML 结构
3. **日志查看**：查看 bot 日志确认模板加载情况

## 最佳实践

1. **保持简洁**：避免过于复杂的设计，确保信息清晰可读
2. **考虑性能**：避免过多的 CSS 动画和特效
3. **测试多用户**：用不同用户的数据测试，确保布局适应各种情况
4. **注释清晰**：在 HTML 中添加注释说明各部分功能
5. **版本控制**：使用语义化版本号（如 1.0.0）

## 提交皮肤

1. 在 `skins/` 目录下创建新目录
2. 编写 HTML 模板文件
3. 测试渲染效果
4. 分享给管理员

## 参考资源

- [Jinja2 文档](https://jinja.palletsprojects.com/)
- [osu! API v2 文档](https://osu.ppy.sh/docs/index.html)
- CSS 渐变生成器：[uiGradients](https://uigradients.com/)
