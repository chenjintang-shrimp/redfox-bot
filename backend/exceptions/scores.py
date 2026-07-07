class ScoreQueryError(Exception):
    """成绩查询失败"""

    template_key = "SCORE_QUERY_ERROR_TEMPLATE"

    def __init__(self, username: str, beatmap_id: int):
        self.username = username
        self.beatmap_id = beatmap_id
        self.error_msg = f"User {username} score query error on beatmap {beatmap_id}"
        super().__init__(self.error_msg)
