from discord.ext.commands import CommandError


class ScoreQueryError(CommandError):
    username: str
    beatmap_id: int
    error_msg: str
    status_code: int

    def __init__(
        self, username: str, beatmap_id: int, error_msg: str, status_code: int
    ):
        self.username = username
        self.beatmap_id = beatmap_id
        self.error_msg = error_msg
        self.status_code = status_code
        super().__init__(
            f"User {self.username} score query error on beatmap {self.beatmap_id}: {error_msg}"
        )
