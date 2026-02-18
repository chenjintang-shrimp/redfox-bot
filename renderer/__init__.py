"""
这一层是在干嘛的呢？让我解释一下。
最开始（也就这个文件出现的一两个commit之前吧），我是直接在后端渲染模板的。
但是我觉得这样做不是很合理，因为后端负责的是业务逻辑，而渲染模板应该是前端的责任。
所以我就把渲染模板这一层抽出来了。很多人说，为什么不在前端做？那我问你，这个 Bot 又要跑 Discord 上又要跑 QQ 上，你觉得，这么复制粘贴合理吗？
准确的说，这里就是大包干，负责统筹调用后端的那些 API，然后把结果渲染成字符串，或者未来可能会加入的图片，返回给前端。前端只要安心发送就可以了。
同时，设计中的 minifilter 也会在这一层被调用。
这一层还有一个作用，就是让我在后端编码的时候注重unix-like的风格，每个函数都是一个小巧锋利的工具，由这一层统筹，组合。就这么简单。

更新（2026-02-18）：
现在这一层已经完全抽象，支持可插拔的渲染引擎。上层只需提供数据，下层自动选择最佳渲染方式
（优先图片，失败时 fallback 到文本），返回统一的 RenderResult。

So, what is the purpose of this layer? Let me explain.

Initially (just a commit or two ago), I was rendering templates directly in the backend.
However, that didn't feel architecturally sound. The backend should be responsible for business logic, while template rendering belongs to the presentation layer.

Thus, I extracted this layer. You might ask, "Why not render in the frontend?"
Well, consider this: this Bot runs on both Discord and QQ. Do you think copy-pasting rendering logic across different platforms is a reasonable practice? (Spoiler: It's not.)

To be precise, this layer acts as an Orchestrator. It coordinates calls to backend APIs, renders the results into strings (or potentially images in the future), and returns the final payload to the frontend. The frontend's only job is to send it out—clean and simple.

Additionally, the planned `minifilter` will also be invoked at this layer.

Finally, this layer enforces a Unix-like philosophy in my backend coding: ensuring every function is a small, sharp, single-purpose tool. This layer then coordinates and composes them. Simple as that.

Update (2026-02-18):
Now this layer is fully abstracted with pluggable render engines. The upper layer just provides data,
and the lower layer automatically selects the best rendering method (image preferred, fallback to text),
returning a unified RenderResult.
"""

# 核心抽象
from renderer.core import (
    NoRendererAvailableError,
    RenderAdapter,
    RenderEngine,
    RenderResult,
)

# 渲染服务
from renderer.service import RenderService, init_render_service, render_service

# 适配器
from renderer.adapters import HtmlImageAdapter, TextAdapter

# 原有的渲染函数（保持向后兼容）
from renderer.scores import (
    render_score_list_image,
    render_today_bp_image,
    render_user_beatmap_score_card,
    render_user_recent_score_card,
    render_user_score_list_image,
    render_user_today_bp_image,
)
from renderer.user import (
    render_binding_user,
    render_unbinding_user,
    render_user_card_image,
    render_user_info,
)
from renderer.beatmap import (
    render_beatmap_card_image,
    render_beatmap_info,
)

__all__ = [
    # 核心抽象
    "RenderResult",
    "RenderEngine",
    "RenderAdapter",
    "NoRendererAvailableError",
    # 渲染服务
    "RenderService",
    "render_service",
    "init_render_service",
    # 适配器
    "HtmlImageAdapter",
    "TextAdapter",
    # 成绩渲染
    "render_user_beatmap_score_card",
    "render_user_recent_score_card",
    "render_user_score_list_image",
    "render_user_today_bp_image",
    "render_score_list_image",
    "render_today_bp_image",
    # 用户渲染
    "render_user_info",
    "render_user_card_image",
    "render_binding_user",
    "render_unbinding_user",
    # 谱面渲染
    "render_beatmap_info",
    "render_beatmap_card_image",
]
