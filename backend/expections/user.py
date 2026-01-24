from discord.ext.commands import CommandError

class UserQueryError(CommandError):
    username: str
    error_msg: str
    status_code: int
    def __init__(self, username: str, error_msg: str, status_code: int):
        self.username = username
        self.error_msg = error_msg
        self.status_code = status_code
        super().__init__(f"User {username} query error: {error_msg}")

class BindExistError(CommandError):
    username: str
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User {username} bind exist error")

class UserNotBindError(CommandError):
    def __init__(self, user_context: str):
        self.user_context = user_context
        super().__init__(f"User {user_context} is not bound.")