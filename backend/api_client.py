from typing import Optional, Dict, Any, Union
from httpx import AsyncClient, Response, HTTPStatusError
from utils.logger import get_logger
import json


class APIClient:
    """
    通用的API调用器类，支持异步HTTP请求
    """
    
    def __init__(self, base_url: str = "", timeout: float = 30.0, headers: Optional[Dict[str, str]] = None):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            headers: 默认请求头
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = headers or {}
        self.logger = get_logger("api_client")
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整的URL"""
        if endpoint.startswith('http'):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None, **kwargs) -> Response:
        """发送GET请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self.logger.info(f"GET {url} - Params: {params}")
        
        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=request_headers, **kwargs)
            self._log_response(response)
            return response
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                   json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, 
                   **kwargs) -> Response:
        """发送POST请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self.logger.info(f"POST {url} - Data: {data} - JSON: {json_data}")
        
        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, data=data, json=json_data, headers=request_headers, **kwargs)
            self._log_response(response)
            return response
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                  json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, 
                  **kwargs) -> Response:
        """发送PUT请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self.logger.info(f"PUT {url} - Data: {data} - JSON: {json_data}")
        
        async with AsyncClient(timeout=self.timeout) as client:
            response = await client.put(url, data=data, json=json_data, headers=request_headers, **kwargs)
            self._log_response(response)
            return response
    
    async def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Response:
        """发送DELETE请求"""
        url = self._build_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        self.logger.info(f"DELETE {url}")
        
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
from utils.variable import API_URL

# 默认的osu! API客户端
def get_osu_api_client() -> APIClient:
    """获取osu! API客户端"""
    return APIClient(
        base_url=API_URL,
        headers={
            "User-Agent": "g0v0bot-discord/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=30.0
    )


# 简化的API调用函数
async def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None, **kwargs) -> Response:
    """简单的GET请求函数"""
    client = get_osu_api_client()
    return await client.get(endpoint, params=params, headers=headers, **kwargs)


async def api_post(endpoint: str, data: Optional[Dict[str, Any]] = None, 
                   json_data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, 
                   **kwargs) -> Response:
    """简单的POST请求函数"""
    client = get_osu_api_client()
    return await client.post(endpoint, data=data, json_data=json_data, headers=headers, **kwargs)