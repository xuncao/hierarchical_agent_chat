"""LLM客户端封装"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import ChatGenerationChunk

from src.config.settings import settings
from src.models.base_models import ModelProvider

logger = logging.getLogger(__name__)


class StreamingCallbackHandler(AsyncCallbackHandler):
    """流式回调处理器"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
    
    async def on_chat_model_start(self, *args, **kwargs):
        """聊天模型开始"""
        pass
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """新token回调"""
        await self.queue.put(token)
    
    async def on_llm_end(self, response, **kwargs) -> None:
        """LLM结束回调"""
        self.done.set()
    
    async def on_llm_error(self, error, **kwargs) -> None:
        """LLM错误回调"""
        logger.error(f"LLM错误: {error}")
        self.done.set()
    
    async def stream_tokens(self) -> AsyncGenerator[str, None]:
        """流式生成token"""
        while not self.done.is_set() or not self.queue.empty():
            try:
                # 设置超时避免无限等待
                token = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                yield token
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue


class LLMClient:
    """LLM客户端封装类"""
    
    def __init__(self):
        self._clients: Dict[str, Any] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化LLM客户端"""
        # DeepSeek客户端
        if settings.DEEPSEEK_API_KEY:
            self._clients[ModelProvider.DEEPSEEK] = ChatOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                model_name=settings.DEFAULT_MODEL_NAME,
                temperature=0.7,
                max_tokens=2000,
                streaming=True
            )
            logger.info("DeepSeek客户端初始化成功")
        
        # Cohere客户端
        if settings.COHERE_API_KEY:
            self._clients[ModelProvider.COHERE] = ChatCohere(
                cohere_api_key=settings.COHERE_API_KEY,
                model="command-r-plus",
                temperature=0.7,
                max_tokens=2000
            )
            logger.info("Cohere客户端初始化成功")
    
    def get_client(self, provider: ModelProvider, model_name: Optional[str] = None) -> Any:
        """获取指定提供商的客户端"""
        if provider not in self._clients:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        client = self._clients[provider]
        
        # 如果指定了模型名称，更新客户端配置
        if model_name:
            if hasattr(client, 'model_name'):
                client.model_name = model_name
            elif hasattr(client, 'model'):
                client.model = model_name
        
        return client
    
    async def generate_response(
        self,
        messages: List[BaseMessage],
        provider: ModelProvider = ModelProvider.DEEPSEEK,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        streaming: bool = False
    ) -> Any:
        """生成响应"""
        try:
            client = self.get_client(provider, model_name)
            
            # 更新配置
            if hasattr(client, 'temperature'):
                client.temperature = temperature
            if hasattr(client, 'max_tokens'):
                client.max_tokens = max_tokens
            if hasattr(client, 'streaming'):
                client.streaming = streaming
            
            if streaming:
                return await self._generate_streaming_response(client, messages)
            else:
                return await self._generate_normal_response(client, messages)
                
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            raise
    
    async def _generate_normal_response(self, client: Any, messages: List[BaseMessage]) -> str:
        """生成普通响应"""
        try:
            response = await client.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"普通响应生成失败: {e}")
            raise
    
    async def _generate_streaming_response(
        self, 
        client: Any, 
        messages: List[BaseMessage]
    ) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        callback_handler = StreamingCallbackHandler()
        
        try:
            # 启动异步流式生成
            task = asyncio.create_task(
                client.ainvoke(messages, callbacks=[callback_handler])
            )
            
            # 流式返回token
            async for token in callback_handler.stream_tokens():
                yield token
            
            # 等待任务完成
            await task
            
        except Exception as e:
            logger.error(f"流式响应生成失败: {e}")
            raise
        finally:
            callback_handler.done.set()
    
    def is_provider_available(self, provider: ModelProvider) -> bool:
        """检查提供商是否可用"""
        return provider in self._clients
    
    def get_available_providers(self) -> List[ModelProvider]:
        """获取可用的提供商列表"""
        return list(self._clients.keys())
    
    async def test_connection(self, provider: ModelProvider) -> bool:
        """测试连接"""
        try:
            client = self.get_client(provider)
            # 发送一个简单的测试消息
            test_message = HumanMessage(content="Hello")
            response = await client.ainvoke([test_message])
            return response.content is not None
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False


# 全局LLM客户端实例
llm_client = LLMClient()