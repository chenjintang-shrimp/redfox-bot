from discord.ext.commands import CommandError


class BeatmapNotFoundError(CommandError):
    beatmap_id: int

    def __init__(self, beatmap_id: int):
        self.beatmap_id = beatmap_id
        super().__init__(f"Beatmap {beatmap_id} not found")
