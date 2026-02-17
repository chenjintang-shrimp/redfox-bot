class UserQueryError(Exception):
    """查询用户失败"""

    template_key = "USER_NOT_FOUND_TEMPLATE"

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User {username} not found")


class BindExistError(Exception):
    """用户已绑定"""

    template_key = "USER_BIND_EXISTING_TEMPLATE"

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User {username} already bound")


class UserNotBindError(Exception):
    """用户未绑定"""

    template_key = "USER_NOT_BOUND_TEMPLATE"

    def __init__(self, user_context: str = ""):
        self.user_context = user_context
        super().__init__(f"User {user_context} is not bound")
