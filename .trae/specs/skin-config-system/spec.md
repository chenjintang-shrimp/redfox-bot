# Skin 配置系统重构 Spec

## Why

当前的 skin 系统使用硬编码的模板名称映射，缺乏灵活性。皮肤作者无法自定义 renderer 到模板的映射关系，也无法为皮肤添加元数据。需要引入 YAML 配置文件来提供更好的灵活性和可扩展性。

## What Changes

- 在每个 skin 目录下引入 `skin.yaml` 配置文件
- 支持 renderer 名称到模板文件的映射配置
- 支持皮肤元数据（名称、版本、作者、描述）
- 向后兼容：无配置文件的皮肤使用默认命名约定

## Impact

- Affected code: `renderer/skin_loader.py`
- Affected docs: `docs/skin_guide.md`

## ADDED Requirements

### Requirement: Skin 配置文件支持

系统应支持在每个 skin 目录下读取 `skin.yaml` 配置文件，用于定义 renderer 到模板的映射关系。

#### Scenario: 有配置文件的皮肤

- **WHEN** skin 目录下存在 `skin.yaml` 文件
- **THEN** 系统根据配置文件中的 `templates` 字段查找对应的模板文件

#### Scenario: 无配置文件的皮肤（向后兼容）

- **WHEN** skin 目录下不存在 `skin.yaml` 文件
- **THEN** 系统使用默认命名约定：`{renderer_name}.html`

### Requirement: Renderer 名称定义

Renderer 名称应使用 `@renderer("name")` 装饰器中定义的字符串，而非函数名。

当前已定义的 renderer 名称：

- `user_card` - 用户卡片
- `user_beatmap_score_card` - 用户在指定谱面的成绩卡片
- `user_recent_score_card` - 用户最近成绩卡片
- `user_score_list` - 用户成绩列表
- `user_today_bp` - 今日 BP
- `beatmap_card` - 谱面卡片

### Requirement: 配置文件格式

`skin.yaml` 应支持以下字段：

```yaml
name: "皮肤名称"
version: "1.0.0"
author: "作者"
description: "描述"

templates:
  user_card: "user_card.html"
  user_beatmap_score_card: "score_card.html"
  user_recent_score_card: "score_card.html"
  user_score_list: "score_list.html"
  user_today_bp: "today_bp.html"
  beatmap_card: "beatmap_card.html"
```

### Requirement: 模板查找优先级

模板查找应遵循以下优先级：

1. 读取 `skin.yaml` 中的 `templates` 映射
2. Fallback: 默认命名约定 `{renderer_name}.html`
3. Fallback: default skin 的配置或默认模板
