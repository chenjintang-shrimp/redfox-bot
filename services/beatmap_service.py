"""谱面服务 - 平台无关的谱面业务逻辑"""

from dataclasses import dataclass
from typing import Optional

from backend.beatmap import get_beatmap_info as _get_beatmap_info
from backend.exceptions.beatmap import BeatmapNotFoundError


@dataclass(frozen=True, slots=True)
class BeatmapInfo:
    """谱面信息数据对象"""

    id: int
    beatmapset_id: int
    title: str
    version: str
    artist: str
    creator: str
    difficulty_rating: float
    bpm: float
    total_length: int
    hit_length: int
    cs: float
    ar: float
    od: float
    hp: float
    mode: str
    status: str
    url: str
    cover_url: str

    @classmethod
    def from_api_response(cls, data: dict) -> "BeatmapInfo":
        """从API响应创建BeatmapInfo"""
        beatmapset = data.get("beatmapset", {})

        # 计算BPM (可能是一个范围)
        bpm_raw = data.get("bpm", 0.0)
        bpm_val: float
        if isinstance(bpm_raw, (list, tuple)) and bpm_raw:
            bpm_val = float(bpm_raw[0]) if bpm_raw[0] else 0.0
        elif isinstance(bpm_raw, (int, float)):
            bpm_val = float(bpm_raw)
        else:
            bpm_val = 0.0

        return cls(
            id=data["id"],
            beatmapset_id=data.get("beatmapset_id", 0),
            title=beatmapset.get("title", data.get("title", "Unknown")),
            version=data.get("version", "Unknown"),
            artist=beatmapset.get("artist", data.get("artist", "Unknown")),
            creator=beatmapset.get("creator", data.get("creator", "Unknown")),
            difficulty_rating=data.get("difficulty_rating", 0.0),
            bpm=bpm_val,
            total_length=data.get("total_length", 0),
            hit_length=data.get("hit_length", 0),
            cs=data.get("cs", 0.0),
            ar=data.get("ar", 0.0),
            od=data.get("accuracy", 0.0),  # API中accuracy就是OD
            hp=data.get("drain", 0.0),  # API中drain就是HP
            mode=data.get("mode", "osu"),
            status=data.get("status", "unknown"),
            url=data.get("url", f"https://osu.ppy.sh/beatmaps/{data['id']}"),
            cover_url=beatmapset.get("covers", {}).get("cover", ""),
        )

    @property
    def formatted_length(self) -> str:
        """格式化时长为 mm:ss"""
        minutes, seconds = divmod(self.hit_length, 60)
        return f"{minutes}:{seconds:02d}"

    @property
    def formatted_bpm(self) -> str:
        """格式化BPM"""
        return f"{self.bpm:.0f}" if self.bpm == int(self.bpm) else f"{self.bpm:.2f}"

    @property
    def star_rating_formatted(self) -> str:
        """格式化星级"""
        return f"{self.difficulty_rating:.2f}"


class BeatmapService:
    """谱面服务类

    提供平台无关的谱面相关业务逻辑
    """

    @staticmethod
    async def get_beatmap(beatmap_id: int) -> BeatmapInfo:
        """获取谱面信息

        Args:
            beatmap_id: 谱面ID

        Returns:
            BeatmapInfo: 谱面信息对象

        Raises:
            BeatmapNotFoundError: 谱面不存在
        """
        data = await _get_beatmap_info(beatmap_id)
        return BeatmapInfo.from_api_response(data)

    @staticmethod
    async def get_beatmap_or_none(beatmap_id: int) -> Optional[BeatmapInfo]:
        """获取谱面信息，不存在返回None

        Args:
            beatmap_id: 谱面ID

        Returns:
            BeatmapInfo | None: 谱面信息或None
        """
        try:
            return await BeatmapService.get_beatmap(beatmap_id)
        except BeatmapNotFoundError:
            return None
