import time
import base64
from typing import Optional, Dict, Any
from httpx import AsyncClient, Response
from utils.logger import get_logger
from utils.scheduler_registry import register
from utils.variable import API_URL, OAUTH_APP_ID, OAUTH_SECRET, OAUTH_TOKEN_TTL
from utils.caches import get_cache, set_cache


class OAuth2Handler:
    """
    OAuth2 验证处理器，处理 client_credentials 流程
    使用缓存系统存储 token，支持多实例共享
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.logger = get_logger("oauth2_handler")

    @property
    def _cache_key(self) -> str:
        """生成缓存 key"""
        return f"oauth:token:{self.client_id}"

    async def get_access_token(self) -> str:
        """获取有效的访问令牌"""
        cached = await get_cache(self._cache_key)

        if cached:
            token = cached.get("token")
            expires_at = cached.get("expires_at", 0)
            # 提前30秒刷新
            if token and time.time() < expires_at - 30:
                return token

        return await self.refresh_token()

    async def refresh_token(self) -> str:
        """从服务器刷新访问令牌并缓存"""
        self.logger.info("Refreshing OAuth2 token...")
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }

        auth_str = f"{self.client_id}:{self.client_secret}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with AsyncClient() as client:
            response = await client.post(self.token_url, data=data, headers=headers)
            if response.status_code != 200:
                self.logger.error(
                    f"Failed to fetch token: {response.status_code} - {response.text}"
                )
                raise Exception(f"OAuth2 token fetch failed: {response.text}")

            result = response.json()
            token = result["access_token"]
            expires_in = result.get("expires_in", 3600)
            expires_at = time.time() + expires_in

            # 缓存 token
            await set_cache(self._cache_key, {
                "token": token,
                "expires_at": expires_at
            }, ttl=expires_in)

            self.logger.info(f"Token refreshed successfully. Expires in {expires_in}s")
            return token


# 全局 OAuth handler 实例（用于定时任务）
_oauth_handler: Optional[OAuth2Handler] = None


def _get_global_oauth_handler() -> OAuth2Handler:
    """获取全局 OAuth handler（内部使用）"""
    global _oauth_handler
    if _oauth_handler is None:
        token_url = f"{API_URL}/oauth/token"
        _oauth_handler = OAuth2Handler(OAUTH_APP_ID, OAUTH_SECRET, token_url)
    return _oauth_handler


@register(name="refresh_token", interval=OAUTH_TOKEN_TTL // 2)
async def scheduled_refresh_token():
    """
    定时刷新 OAuth token
    间隔为 TTL 的一半，确保 token 不会过期
    """
    handler = _get_global_oauth_handler()
    # get_access_token 内部会检查是否需要刷新
    await handler.get_access_token()


class APIClient:
    """
    通用的API调用器类，支持异步HTTP请求
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        oauth_handler: Optional[OAuth2Handler] = None,
    ):
        """
        初始化API客户端

        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            headers: 默认请求头
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self.oauth_handler = oauth_handler
        self.logger = get_logger("api_client")

    def _build_url(self, endpoint: str) -> str:
        """构建完整的URL"""
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """发送GET请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}

        self.logger.info(f"GET {url} - Params: {params}")

        if self.oauth_handler:
            token = await self.oauth_handler.get_access_token()
            request_headers["Authorization"] = f"Bearer {token}"

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url, params=params, headers=request_headers, **kwargs
            )
            self._log_response(response)
            return response

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """发送POST请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}

        self.logger.info(f"POST {url} - Data: {data} - JSON: {json_data}")

        if self.oauth_handler:
            token = await self.oauth_handler.get_access_token()
            request_headers["Authorization"] = f"Bearer {token}"

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url, data=data, json=json_data, headers=request_headers, **kwargs
            )
            self._log_response(response)
            return response

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Response:
        """发送PUT请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}

        self.logger.info(f"PUT {url} - Data: {data} - JSON: {json_data}")

        if self.oauth_handler:
            token = await self.oauth_handler.get_access_token()
            request_headers["Authorization"] = f"Bearer {token}"

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                url, data=data, json=json_data, headers=request_headers, **kwargs
            )
            self._log_response(response)
            return response

    async def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> Response:
        """发送DELETE请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}

        self.logger.info(f"DELETE {url}")

        if self.oauth_handler:
            token = await self.oauth_handler.get_access_token()
            request_headers["Authorization"] = f"Bearer {token}"

        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(url, headers=request_headers, **kwargs)
            self._log_response(response)
            return response

    def _log_response(self, response: Response):
        """记录响应信息"""
        self.logger.info(f"Response: {response.status_code} - {response.url}")
        if response.status_code >= 400:
            self.logger.warning(f"Error response: {response.text[:200]}")

    @staticmethod
    def is_success(response: Response) -> bool:
        """检查响应是否成功"""
        return 200 <= response.status_code < 300

    @staticmethod
    async def get_json(response: Response) -> Dict[str, Any]:
        """从响应中获取JSON数据"""
        try:
            return response.json()
        except Exception as e:
            get_logger("api_client").error(f"Failed to parse JSON: {e}")
            return {}


# 创建默认的API客户端实例


# 默认的osu! API客户端
def get_osu_api_client() -> APIClient:
    """获取osu! API客户端"""
    # 自动创建 OAuth2Handler
    oauth_handler = None
    if OAUTH_APP_ID and OAUTH_SECRET:
        oauth_handler = OAuth2Handler(
            client_id=str(OAUTH_APP_ID),
            client_secret=OAUTH_SECRET,
            token_url=f"{API_URL.rstrip('/')}/oauth/token",
        )

    return APIClient(
        base_url=API_URL,
        headers={
            "User-Agent": "g0v0bot-discord/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=30.0,
        oauth_handler=oauth_handler,
    )
