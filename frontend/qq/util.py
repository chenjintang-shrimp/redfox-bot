from backend.database import get_osu_user_by_qq_id
from backend.expections.user import UserNotBindError


async def resolve_username_qq(qq_id: int, username_arg: str | None) -> str:
    """
    解析用户名
    Args:
        qq_id: QQ号
        username_arg: 用户提供的用户名参数
    Returns:
        解析后的用户名
    Raises:
        UserNotBindError: 如果没有提供用户名且未绑定
    """
    if username_arg:
        return username_arg.strip()

    osu_user = await get_osu_user_by_qq_id(qq_id)
    if osu_user is None:
        raise UserNotBindError(str(qq_id))

    return osu_user.osu_username
