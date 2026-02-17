"""成绩服务 - 平台无关的成绩业务逻辑"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from backend.scores import (
    get_user_beatmap_score as _get_user_beatmap_score,
    get_user_beatmap_all_scores as _get_user_beatmap_all_scores,
    get_user_scores as _get_user_scores,
)
from backend.exceptions.scores import ScoreQueryError


@dataclass(frozen=True, slots=True)
class ScoreInfo:
    """成绩信息数据对象"""

    id: int
    user_id: int
    beatmap_id: int
    total_score: int
    accuracy: float
    max_combo: int
    rank: str
    rank_emoji: str
    pp: float
    mods: list[str]
    created_at: datetime
    beatmap: dict
    beatmapset: dict
    statistics: dict
    perfect: bool

    @classmethod
    def from_api_response(cls, data: dict) -> "ScoreInfo":
        """从API响应创建ScoreInfo"""
        from utils.strings import load_strings

        rank = data.get("rank", "F")
        rank_emojis = load_strings().get("RANK_EMOJIS", {})
        rank_emoji = rank_emojis.get(rank, f"[{rank}]")

        # 解析时间
        created_at_str = data.get("created_at", "")
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            created_at = datetime.now()

        return cls(
            id=data.get("id", 0),
            user_id=data.get("user_id", 0),
            beatmap_id=data.get("beatmap_id", 0),
            total_score=data.get("total_score", 0),
            accuracy=data.get("accuracy", 0.0),
            max_combo=data.get("max_combo", 0),
            rank=rank,
            rank_emoji=rank_emoji,
            pp=data.get("pp", 0.0) or 0.0,
            mods=data.get("mods", []),
            created_at=created_at,
            beatmap=data.get("beatmap", {}),
            beatmapset=data.get("beatmapset", {}),
            statistics=data.get("statistics", {}),
            perfect=data.get("perfect", False),
        )


@dataclass(frozen=True, slots=True)
class ScoreListResult:
    """成绩列表结果"""

    scores: list[ScoreInfo]
    total: int
    has_more: bool


class ScoreService:
    """成绩服务类

    提供平台无关的成绩相关业务逻辑
    """

    SCORES_PER_PAGE = 10

    @staticmethod
    async def get_beatmap_score(user_id: int, beatmap_id: int) -> ScoreInfo:
        """获取用户在特定谱面的成绩

        Args:
            user_id: 用户ID
            beatmap_id: 谱面ID

        Returns:
            ScoreInfo: 成绩信息

        Raises:
            ScoreQueryError: 查询失败
        """
        data = await _get_user_beatmap_score(user_id, beatmap_id)
        if isinstance(data, list) and data:
            return ScoreInfo.from_api_response(data[0])
        elif isinstance(data, dict):
            return ScoreInfo.from_api_response(data)
        raise ScoreQueryError(str(user_id), beatmap_id)

    @staticmethod
    async def get_beatmap_all_scores(
        user_id: int, beatmap_id: int, ruleset: Optional[str] = None
    ) -> ScoreListResult:
        """获取用户在特定谱面的所有成绩

        Args:
            user_id: 用户ID
            beatmap_id: 谱面ID
            ruleset: 游戏模式 (可选)

        Returns:
            ScoreListResult: 成绩列表结果
        """
        scores_data = await _get_user_beatmap_all_scores(user_id, beatmap_id, ruleset)
        scores = [ScoreInfo.from_api_response(s) for s in scores_data]
        return ScoreListResult(
            scores=scores,
            total=len(scores),
            has_more=False,
        )

    @staticmethod
    async def get_user_score_list(
        user_id: int,
        score_type: str,
        *,
        include_fails: bool = False,
        mode: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> ScoreListResult:
        """获取用户成绩列表

        Args:
            user_id: 用户ID
            score_type: 成绩类型 (best/recent/firsts/pinned)
            include_fails: 是否包含失败成绩
            mode: 游戏模式
            page: 页码 (从1开始)
            limit: 每页数量

        Returns:
            ScoreListResult: 成绩列表结果
        """
        offset = (page - 1) * limit
        scores_data = await _get_user_scores(
            user_id,
            score_type,
            include_fails=include_fails,
            mode=mode,
            limit=limit,
            offset=offset,
        )

        if not isinstance(scores_data, list):
            scores_data = []

        scores = [ScoreInfo.from_api_response(s) for s in scores_data]

        # 判断是否还有更多
        has_more = len(scores_data) >= limit

        return ScoreListResult(
            scores=scores,
            total=len(scores),
            has_more=has_more,
        )

    @staticmethod
    async def get_page_count(user_id: int, beatmap_id: int) -> int:
        """获取谱面成绩的页数

        Args:
            user_id: 用户ID
            beatmap_id: 谱面ID

        Returns:
            int: 总页数
        """
        try:
            result = await ScoreService.get_beatmap_all_scores(user_id, beatmap_id)
            return max(
                1,
                (result.total + ScoreService.SCORES_PER_PAGE - 1)
                // ScoreService.SCORES_PER_PAGE,
            )
        except ScoreQueryError:
            return 1

    @staticmethod
    async def get_user_scores_page_count(
        user_id: int,
        score_type: str,
        include_fails: bool = False,
        mode: Optional[str] = None,
    ) -> int:
        """获取用户成绩列表的页数

        Args:
            user_id: 用户ID
            score_type: 成绩类型
            include_fails: 是否包含失败成绩
            mode: 游戏模式

        Returns:
            int: 总页数 (默认返回1，实际应根据API返回的总数计算)
        """
        # 先获取第一页，根据返回判断是否还有更多
        result = await ScoreService.get_user_score_list(
            user_id,
            score_type,
            include_fails=include_fails,
            mode=mode,
            page=1,
            limit=100,  # 获取较多数据来估算
        )
        return max(
            1,
            (result.total + ScoreService.SCORES_PER_PAGE - 1)
            // ScoreService.SCORES_PER_PAGE,
        )

    @staticmethod
    def filter_today_bp(scores: list[ScoreInfo]) -> list[ScoreInfo]:
        """筛选今日BP (24小时内)

        Args:
            scores: 成绩列表

        Returns:
            list[ScoreInfo]: 今日的成绩列表
        """
        from datetime import timedelta

        now = datetime.now()
        cutoff = now - timedelta(hours=24)

        return [s for s in scores if s.created_at >= cutoff]
