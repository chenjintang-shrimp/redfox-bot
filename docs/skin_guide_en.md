Here is the English translation of the Skin Creation Guide.

---

# Skin Creation Guide

## Overview

The Skin system is a template system based on HTML/CSS, utilizing **Jinja2** as the template engine. This guide will assist you in creating aesthetically pleasing and efficient skins.

## Directory Structure

```
skins/
└── your_skin/                # Skin directory name
    ├── user_card.html        # User card template
    ├── score_card.html       # Score card template
    └── style.css             # (Optional) Style file
```

## Basic Principles

### 1. Prioritize Official API Fields

**Recommended Practice:**

```html
<!-- Use raw API fields directly -->
<div class="username">{{ username }}</div>
<div class="country">{{ country.name }}</div>
<div class="pp">{{ statistics.pp }}</div>
```

**Not Recommended:**

```html
<!-- Do not create minifilters just for custom field names -->
<div class="pp">{{ pp_formatted }}</div>  <!-- Requires minifilter conversion -->
```

**Exceptions:** Only use minifilters when complex calculation or formatting is required.

### 2. Leverage Jinja2 Features

#### Filters

```html
<!-- Numeric Formatting -->
<div class="pp">{{ statistics.pp | int }}</div>
<div class="accuracy">{{ statistics.hit_accuracy | round(2) }}%</div>

<!-- String Processing -->
<div class="username">{{ username | upper }}</div>
<div class="title">{{ beatmap.title | truncate(30) }}</div>

<!-- Default Values -->
<div class="rank">#{{ statistics.global_rank | default('N/A') }}</div>

<!-- List Operations -->
<div class="mods">{{ mods | join(', ') }}</div>
```

#### Conditionals

```html
{% if statistics.global_rank %}
    <div class="rank">#{{ statistics.global_rank }}</div>
{% else %}
    <div class="rank">Unranked</div>
{% endif %}

<!-- Shorthand Syntax -->
<div class="rank">{{ '#' ~ statistics.global_rank if statistics.global_rank else 'Unranked' }}</div>
```

#### Loops

```html
<!-- Iterate through score list -->
{% for score in scores %}
    <div class="score-item">
        <span>{{ score.rank }}</span>
        <span>{{ score.pp | round(2) }}pp</span>
    </div>
{% endfor %}

<!-- With Index -->
{% for score in scores %}
    <div class="score-item">
        <span>#{{ loop.index }}</span>
        <span>{{ score.rank }}</span>
    </div>
{% endfor %}
```

#### Macros

```html
<!-- Define Macro -->
{% macro render_stat(label, value, unit='') %}
    <div class="stat">
        <div class="stat-value">{{ value }}{{ unit }}</div>
        <div class="stat-label">{{ label }}</div>
    </div>
{% endmacro %}

<!-- Use Macro -->
{{ render_stat('PP', statistics.pp | int) }}
{{ render_stat('Accuracy', statistics.hit_accuracy | round(2), '%') }}
```

### 3. Inline Styles vs. External Styles

**Recommended: Inline Styles**

```html
<style>
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
    }
</style>
<div class="card">
    <!-- Content -->
</div>
```

**Reasons:**

- A single file is enough to complete a skin.
- Easier to share and install.
- No extra requests for CSS files during rendering.

### 4. Layout Design

```html
<style>
    .card {
        width: 800px;
        height: 400px;
        /* Fixed size ensures consistent screenshots */
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

## Available Data Fields

All fields come from **osu! API v2** (osu-web).

### User Card (user_card)

```html
<!-- Basic Info -->
{{ id }}                    <!-- User ID -->
{{ username }}              <!-- Username -->
{{ avatar_url }}            <!-- Avatar URL -->
{{ cover_url }}             <!-- Cover URL -->
{{ join_date }}             <!-- Registration Date -->

<!-- Country Info -->
{{ country.code }}          <!-- Country Code (e.g., "JP") -->
{{ country.name }}          <!-- Country Name (e.g., "Japan") -->

<!-- Game Mode -->
{{ playmode }}              <!-- Current Mode (osu/taiko/catch/mania) -->

<!-- Statistics -->
{{ statistics.pp }}                     <!-- PP -->
{{ statistics.global_rank }}            <!-- Global Rank -->
{{ statistics.country_rank }}           <!-- Country Rank -->
{{ statistics.hit_accuracy }}           <!-- Accuracy -->
{{ statistics.play_count }}             <!-- Play Count -->
{{ statistics.play_time }}              <!-- Play Time (seconds) -->
{{ statistics.maximum_combo }}          <!-- Max Combo -->
{{ statistics.total_hits }}             <!-- Total Hits -->
{{ statistics.ranked_score }}           <!-- Ranked Score -->
{{ statistics.total_score }}            <!-- Total Score -->

<!-- Level Info -->
{{ statistics.level.current }}          <!-- Current Level -->
{{ statistics.level.progress }}         <!-- Level Progress (0-100) -->

<!-- Grade Counts -->
{{ statistics.grade_counts.ss }}        <!-- SS Count -->
{{ statistics.grade_counts.ssh }}       <!-- SSH Count -->
{{ statistics.grade_counts.s }}         <!-- S Count -->
{{ statistics.grade_counts.sh }}        <!-- SH Count -->
{{ statistics.grade_counts.a }}         <!-- A Count -->
```

### Score Card (score_card)

```html
<!-- Basic Info -->
{{ id }}                    <!-- Score ID -->
{{ user_id }}               <!-- User ID -->
{{ accuracy }}              <!-- Accuracy -->
{{ mods }}                  <!-- Mods List -->
{{ score }}                 <!-- Score -->
{{ max_combo }}             <!-- Max Combo -->
{{ passed }}                <!-- Passed State -->
{{ pp }}                    <!-- PP -->
{{ rank }}                  <!-- Grade (XH/X/SH/S/A/B/C/D) -->
{{ created_at }}            <!-- Score Date -->

<!-- Beatmap Info -->
{{ beatmap.id }}
{{ beatmap.beatmapset_id }}
{{ beatmap.version }}       <!-- Difficulty Name -->
{{ beatmap.difficulty_rating }}  <!-- Star Rating -->
{{ beatmap.mode }}
{{ beatmap.total_length }}
{{ beatmap.hit_length }}
{{ beatmap.bpm }}
{{ beatmap.cs }}
{{ beatmap.drain }}
{{ beatmap.accuracy }}      <!-- OD -->
{{ beatmap.ar }}

<!-- Beatmapset Info -->
{{ beatmapset.title }}
{{ beatmapset.artist }}
{{ beatmapset.creator }}    <!-- Mapper Username -->
{{ beatmapset.status }}     <!-- ranked/approved/loved etc. -->

<!-- Statistics -->
{{ statistics.count_300 }}
{{ statistics.count_100 }}
{{ statistics.count_50 }}
{{ statistics.count_miss }}
{{ statistics.count_geki }}     <!-- Mania Perfect -->
{{ statistics.count_katu }}     <!-- Mania Good -->
```

## Complete Example

### Minimalist User Card

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
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
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

## Debugging Tips

1. **View Available Fields**: Add `{{ data | tojson }}` to your template to dump all available data.
2. **Check Rendering**: Use your browser's developer tools to inspect the generated HTML structure.
3. **Check Logs**: View bot logs to confirm if the template loaded successfully.

## Best Practices

1. **Keep it Simple**: Avoid overly complex designs; ensure information is clear and readable.
2. **Consider Performance**: Avoid excessive CSS animations and effects.
3. **Test Multiple Users**: Test with data from different users to ensure the layout adapts to various scenarios (e.g., long usernames).
4. **Clear Comments**: Add comments in HTML to explain the function of each section.
5. **Version Control**: Use semantic versioning (e.g., 1.0.0).

## Submitting Skins

1. Create a new directory under the `skins/` folder.
2. Write your HTML template files.
3. Test the rendering results.
4. Share with the administrators.

## Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [osu! API v2 Documentation](https://osu.ppy.sh/docs/index.html)
- CSS Gradient Generator: [uiGradients](https://uigradients.com/)
