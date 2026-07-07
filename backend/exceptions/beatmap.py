class BeatmapNotFoundError(Exception):
    """谱面不存在"""

    template_key = "BEATMAP_NOT_FOUND_TEMPLATE"

    def __init__(self, beatmap_id: int):
        self.beatmap_id = beatmap_id
        self.error_msg = f"Beatmap {beatmap_id} not found"
        super().__init__(self.error_msg)
