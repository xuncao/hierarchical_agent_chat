"""聊天相关数据模型"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

from .base_models import MessageRole, AgentType, ModelProvider, StreamingMode, IDMixin, TimestampMixin


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息内容")
    conversation_id: Optional[str] = Field(None, description="对话ID，为空则创建新对话")
    agent_type: AgentType = Field(AgentType.COORDINATOR, description="使用的代理类型")
    model_provider: ModelProvider = Field(ModelProvider.DEEPSEEK, description="模型提供商")
    model_name: str = Field("deepseek-chat", description="模型名称")
    streaming: bool = Field(True, description="是否启用流式输出")
    streaming_mode: StreamingMode = Field(StreamingMode.SSE, description="流式模式")
    max_tokens: int = Field(2000, ge=100, le=4000, description="最大token数")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    use_search: bool = Field(False, description="是否启用联网搜索")
    deep_thought: bool = Field(False, description="是否启用深度思考")
    custom_prompt: Optional[str] = Field(None, description="自定义提示词")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    conversation_id: str = Field(..., description="对话ID")
    message_id: str = Field(..., description="消息ID")
    content: str = Field(..., description="AI回复内容")
    is_complete: bool = Field(..., description="是否完成")
    timestamp: datetime = Field(..., description="响应时间")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="响应元数据")


class StreamingChatResponse(BaseModel):
    """流式聊天响应模型"""
    conversation_id: str = Field(..., description="对话ID")
    message_id: str = Field(..., description="消息ID")
    content: str = Field(..., description="流式内容片段")
    is_complete: bool = Field(..., description="是否完成")
    timestamp: datetime = Field(..., description="响应时间")


class Conversation(IDMixin, TimestampMixin):
    """对话模型"""
    title: str = Field(..., description="对话标题")
    user_id: Optional[str] = Field(None, description="用户ID")
    agent_type: AgentType = Field(..., description="使用的代理类型")
    model_provider: ModelProvider = Field(..., description="模型提供商")
    model_name: str = Field(..., description="模型名称")
    message_count: int = Field(0, description="消息数量")
    is_active: bool = Field(True, description="是否活跃")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="对话元数据")


class ConversationMessage(IDMixin, TimestampMixin):
    """对话消息模型"""
    conversation_id: str = Field(..., description="对话ID")
    role: MessageRole = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    token_count: int = Field(0, description="token数量")
    model_name: str = Field(..., description="使用的模型")
    is_user_message: bool = Field(..., description="是否为用户消息")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="消息元数据")


class ConversationHistory(BaseModel):
    """对话历史模型"""
    conversation: Conversation = Field(..., description="对话信息")
    messages: List[ConversationMessage] = Field(..., description="消息列表")
    total_messages: int = Field(..., description="总消息数")


class ConversationListResponse(BaseModel):
    """对话列表响应模型"""
    conversations: List[Conversation] = Field(..., description="对话列表")
    total: int = Field(..., description="总对话数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")


class AgentStatus(BaseModel):
    """代理状态模型"""
    agent_type: AgentType = Field(..., description="代理类型")
    is_available: bool = Field(..., description="是否可用")
    last_activity: datetime = Field(..., description="最后活动时间")
    queue_size: int = Field(0, description="队列大小")
    error_count: int = Field(0, description="错误计数")


class ModelInfo(BaseModel):
    """模型信息模型"""
    provider: ModelProvider = Field(..., description="模型提供商")
    name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    max_tokens: int = Field(..., description="最大token数")
    is_available: bool = Field(..., description="是否可用")
    supports_streaming: bool = Field(..., description="是否支持流式")
    supports_search: bool = Field(False, description="是否支持搜索")
    description: Optional[str] = Field(None, description="模型描述")


class UsageStats(BaseModel):
    """使用统计模型"""
    total_requests: int = Field(0, description="总请求数")
    successful_requests: int = Field(0, description="成功请求数")
    failed_requests: int = Field(0, description="失败请求数")
    total_tokens: int = Field(0, description="总token数")
    avg_response_time: float = Field(0.0, description="平均响应时间")
    last_updated: datetime = Field(..., description="最后更新时间")