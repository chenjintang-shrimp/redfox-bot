from discord.ext.commands import CommandError

class UserQueryError(CommandError):
    username: str
    error_msg: str
    def __init__(self, username: str, error_msg: str):
        self.username = username
        self.error_msg = error_msg
        super().__init__(f"User {username} query error: {error_msg}")

class BindExistError(CommandError):
    username: str
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User {username} bind exist error")
